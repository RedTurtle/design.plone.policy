# -*- coding: utf-8 -*-
"""Move the base64 images of card and alert blocks to Image contents.

The "testo_riquadro_immagine" and "alert" blocks stored their image inline in
the block data as ``{"data": <base64>, "encoding": "base64", "content-type",
"filename"}``. The new format references an Image content instead, like the
"ctaImage" of the CTA block: ``[{"@id": <resolveuid link>, "image_field":
"image"}]``.

Before creating the Image, big images are resized (max 1600px) and converted to
WebP.
"""

from Acquisition import aq_parent
from design.plone.policy.upgrades import logger
from design.plone.policy.upgrades.base import iter_blocks_candidates
from design.plone.policy.upgrades.base import process_blocks_fields
from io import BytesIO
from PIL import features
from PIL import Image
from PIL import ImageOps
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage
from plone.restapi.blocks import visit_blocks
from plone.restapi.deserializer.utils import path2uid
from Products.CMFCore.interfaces import IFolderish

import base64
import mimetypes
import os

BLOCK_TYPES = ("testo_riquadro_immagine", "alert")
MAX_SIDE = 1600
WEBP_QUALITY = 82
# smaller images within MAX_SIDE are left untouched
MIN_BYTES = 100 * 1024

SKIP_CONTENT_TYPES = ("image/svg+xml",)


def _has_alpha(image):
    if image.mode in ("RGBA", "LA", "PA"):
        return True
    return image.mode == "P" and "transparency" in image.info


def _optimize(raw, content_type, filename):
    """Return ``(new_raw, stats)``, or ``(None, None)`` to keep ``raw``."""
    if content_type in SKIP_CONTENT_TYPES:
        return None, None
    if not features.check("webp"):
        logger.warning("Pillow has no WebP support: block images are not optimized.")
        return None, None

    image = Image.open(BytesIO(raw))
    if getattr(image, "is_animated", False):
        return None, None
    old_size = image.size
    if max(old_size) <= MAX_SIDE and (image.format == "WEBP" or len(raw) < MIN_BYTES):
        return None, None

    # an ICC profile is valid only for the original color space
    icc_profile = (
        image.info.get("icc_profile") if image.mode in ("RGB", "RGBA") else None
    )
    mode = "RGBA" if _has_alpha(image) else "RGB"
    image = ImageOps.exif_transpose(image).convert(mode)
    image.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)

    params = {"quality": WEBP_QUALITY, "method": 4}
    if icc_profile:
        params["icc_profile"] = icc_profile
    out = BytesIO()
    image.save(out, "WEBP", **params)
    new_raw = out.getvalue()
    if len(new_raw) >= len(raw):
        return None, None

    stats = {
        "filename": filename,
        "old_type": content_type,
        "old_size": old_size,
        "old_bytes": len(raw),
        "new_size": image.size,
        "new_bytes": len(new_raw),
    }
    return new_raw, stats


def optimize_image_with_stats(raw, content_type, filename):
    """Resize and convert to WebP the image data ``raw``.

    Return ``(new_raw, stats)``, or ``(None, None)`` if the image does not need
    to be optimized (SVG, animated, small or already WebP within MAX_SIDE).
    Never raises: for an image that cannot be processed, return ``None`` and
    stats with an "error" key.
    """
    try:
        return _optimize(raw, content_type, filename)
    except Exception as e:  # e.g. unknown format, decompression bomb
        logger.warning("Unable to optimize block image %r: %s", filename, e)
        return None, {"filename": filename, "error": str(e)}


def is_legacy_image(value):
    """True if the image is stored inline in the block as base64."""
    if not isinstance(value, dict):
        return False
    return isinstance(value.get("data"), str) and value.get("encoding") == "base64"


def image_container(context):
    """The container of the Image contents used in the blocks of context."""
    if IFolderish.providedBy(context):
        return context
    return aq_parent(context)


def _convert(context, block):
    """Create an Image content with the inline image of the block.

    Return ``(new_value, stats)``.
    """
    value = block["image"]
    raw = base64.b64decode(value["data"])
    if not raw:
        raise ValueError("empty image data")
    content_type = value.get("content-type") or ""
    # the filename can be the url of an image pasted from another site
    filename = (value.get("filename") or "").rsplit("/", 1)[-1]
    title = os.path.splitext(filename)[0] or block.get("image_card_title") or "image"
    if not filename:
        filename = "image" + (mimetypes.guess_extension(content_type) or "")

    new_raw, optimization = optimize_image_with_stats(
        raw, content_type, value.get("filename")
    )
    if new_raw:
        raw = new_raw
        content_type = "image/webp"
        filename = f"{os.path.splitext(filename)[0]}.webp"

    container = image_container(context)
    image = createContentInContainer(
        container,
        "Image",
        checkConstraints=False,
        title=title,
        image=NamedBlobImage(data=raw, filename=filename, contentType=content_type),
    )
    try:
        # the same value stored by the deserializers when the frontend saves
        # the block with "@id" set to the url of the image
        uid_link = path2uid(context=context, link=image.absolute_url())
        if "resolveuid/" not in uid_link:
            raise ValueError(f"unable to get the resolveuid link of {uid_link}")
    except Exception:
        container._delObject(image.getId())
        raise
    new_value = [{"@id": uid_link, "image_field": "image"}]
    stats = {
        "filename": value.get("filename"),
        "bytes": len(raw),
        "path": "/".join(image.getPhysicalPath()),
        "optimization": optimization,
    }
    return new_value, stats


def convert_image_with_stats(context, block):
    """Move the inline image of the block to a new Image content.

    The Image is created in context, or in its parent if context is not
    folderish. Return ``(new_value, stats)``, or ``(None, None)`` if the block
    has no inline image. Never raises: an image that cannot be converted is
    left untouched, and the returned stats contain an "error" key.
    """
    value = block.get("image")
    if not is_legacy_image(value):
        return None, None
    try:
        return _convert(context, block)
    except Exception as e:  # e.g. invalid base64
        filename = value.get("filename")
        logger.warning("Unable to convert block image %r: %s", filename, e)
        return None, {"filename": filename, "error": str(e)}


def convert_blocks(context, blocks):
    """Move to Image contents the inline images of the blocks (nested ones
    included), changing the blocks in place.

    Return a list of stats, one for each converted image and one for each
    image that could not be converted (with an "error" key).
    """
    if not isinstance(blocks, dict):
        return []
    changes = []
    for block in visit_blocks(context, blocks):
        block_type = block.get("@type")
        if block_type not in BLOCK_TYPES:
            continue
        new_value, stats = convert_image_with_stats(context, block)
        if new_value:
            block["image"] = new_value
        if stats:
            stats["block_type"] = block_type
            changes.append(stats)
    return changes


def human_size(size):
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def format_change(stats):
    old_w, old_h = stats["old_size"]
    new_w, new_h = stats["new_size"]
    saved = 100 - stats["new_bytes"] * 100 / stats["old_bytes"]
    return (
        f'{stats["block_type"]} "{stats["filename"]}" {stats["old_type"]} '
        f'{old_w}x{old_h} {human_size(stats["old_bytes"])} -> image/webp '
        f'{new_w}x{new_h} {human_size(stats["new_bytes"])} (-{saved:.0f}%)'
    )


def _log_image(prefix, path, stats):
    optimization = stats.get("optimization")
    if optimization and "error" in optimization:
        logger.warning(
            f'{prefix} {path} - {stats["block_type"]} "{stats["filename"]}" '
            f'not optimized, stored as is: {optimization["error"]}'
        )
    elif optimization:
        optimization["block_type"] = stats["block_type"]
        logger.info(f"{prefix} {path} - optimized {format_change(optimization)}")
    logger.info(
        f'{prefix} {path} - {stats["block_type"]} "{stats["filename"]}" '
        f'{human_size(stats["bytes"])} -> {stats["path"]}'
    )


def to_3106(context):
    """Move the base64 images of card and alert blocks to Image contents."""
    prefix = "[3105 - 3106]"
    modified = []
    errors = []
    optimized = 0
    analyzed = 0
    for path, get_object in iter_blocks_candidates(BLOCK_TYPES, prefix):
        analyzed += 1
        try:
            obj = get_object()
        except (AttributeError, KeyError):
            logger.warning(f"{prefix} {path} - unable to get the object")
            continue
        changes = process_blocks_fields(obj, convert_blocks)
        created = 0
        for stats in changes:
            if "error" in stats:
                errors.append((path, stats))
                logger.warning(
                    f'{prefix} {path} - {stats["block_type"]} "{stats["filename"]}" '
                    f'not converted: {stats["error"]}'
                )
                continue
            created += 1
            optimization = stats["optimization"]
            if optimization and "error" not in optimization:
                optimized += 1
            _log_image(prefix, path, stats)
        if not created:
            continue
        obj.reindexObject()
        modified.append((path, created))
        logger.info(f"{prefix} {path} - {created} images converted")

    logger.info(f"{prefix} ### Block images conversion summary ###")
    logger.info(f"{prefix} Analyzed pages: {analyzed}")
    logger.info(f"{prefix} Modified pages: {len(modified)}")
    logger.info(f"{prefix} Created images: {sum(item[1] for item in modified)}")
    logger.info(f"{prefix} Optimized images: {optimized}")
    logger.info(f"{prefix} Images not converted for errors: {len(errors)}")
    for path, stats in errors:
        logger.info(f'{prefix} Not converted: {path} - "{stats["filename"]}"')

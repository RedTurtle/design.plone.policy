# -*- coding: utf-8 -*-
"""Shrink base64 images stored inline in Volto blocks.

The "testo_riquadro_immagine" and "alert" blocks store their image inline in
the block data as ``{"data": <base64>, "encoding": "base64", "content-type",
"filename"}``. Large uploads make the page payload huge, so we resize them and
re-encode them as WebP.
"""

from io import BytesIO
from PIL import features
from PIL import Image
from PIL import ImageOps
from plone.restapi.blocks import visit_blocks

import base64
import logging
import os

logger = logging.getLogger(__name__)

BLOCK_TYPES = ("testo_riquadro_immagine", "alert")
MAX_SIDE = 1600
WEBP_QUALITY = 82

SKIP_CONTENT_TYPES = ("image/svg+xml",)


def _has_alpha(image):
    if image.mode in ("RGBA", "LA", "PA"):
        return True
    return image.mode == "P" and "transparency" in image.info


def _optimize(value):
    """Return ``(new_value, stats)``, or ``(None, None)`` to keep ``value``."""
    if not isinstance(value, dict):
        return None, None
    data = value.get("data")
    if not data or not isinstance(data, str) or value.get("encoding") != "base64":
        return None, None
    content_type = value.get("content-type", "")
    if content_type in SKIP_CONTENT_TYPES:
        return None, None
    if not features.check("webp"):
        logger.warning("Pillow has no WebP support: block images are not optimized.")
        return None, None

    raw = base64.b64decode(data)
    image = Image.open(BytesIO(raw))
    if getattr(image, "is_animated", False):
        return None, None
    old_size = image.size
    if max(old_size) <= MAX_SIDE and image.format == "WEBP":
        # already optimized
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

    filename = value.get("filename") or "image"
    new_value = dict(value)
    new_value.update(
        {
            "data": base64.b64encode(new_raw).decode("ascii"),
            "encoding": "base64",
            "content-type": "image/webp",
            "filename": f"{os.path.splitext(filename)[0]}.webp",
        }
    )
    stats = {
        "filename": filename,
        "old_type": content_type,
        "old_size": old_size,
        "old_bytes": len(raw),
        "new_size": image.size,
        "new_bytes": len(new_raw),
    }
    return new_value, stats


def optimize_image_with_stats(value):
    """Like ``optimize_image``, but also return the stats of the change.

    Never raises: an image that cannot be processed is left untouched, and the
    returned stats contain an "error" key.
    """
    try:
        return _optimize(value)
    except Exception as e:  # e.g. invalid base64, unknown format, decompression bomb
        filename = value.get("filename") if isinstance(value, dict) else None
        logger.warning("Unable to optimize block image %r: %s", filename, e)
        return None, {"filename": filename, "error": str(e)}


def optimize_image(value):
    """Return an optimized copy of an inline image value, or None to keep it."""
    return optimize_image_with_stats(value)[0]


def optimize_blocks(context, blocks):
    """Optimize in place the inline images of the blocks (nested ones included).

    Return a list of stats, one for each optimized image and one for each
    image that could not be processed (with an "error" key).
    """
    if not isinstance(blocks, dict):
        return []
    changes = []
    for block in visit_blocks(context, blocks):
        block_type = block.get("@type")
        if block_type not in BLOCK_TYPES:
            continue
        new_value, stats = optimize_image_with_stats(block.get("image"))
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

# -*- coding: utf-8 -*-
from collective.volto.blocksfield.interfaces import IBlocksFieldEnabled
from design.plone.policy.testing import DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from design.plone.policy.upgrades.v3106 import convert_blocks
from design.plone.policy.upgrades.v3106 import human_size
from design.plone.policy.upgrades.v3106 import MAX_SIDE
from design.plone.policy.upgrades.v3106 import optimize_image_with_stats
from design.plone.policy.upgrades.v3106 import to_3106
from io import BytesIO
from PIL import Image
from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import RelativeSession
from transaction import commit
from zope.interface import alsoProvides

import base64
import unittest

SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>'


def noise_image(width, height, mode="RGB"):
    image = Image.merge(
        "RGB", [Image.effect_noise((width, height), 40) for _ in range(3)]
    )
    if mode == "RGBA":
        image.putalpha(Image.linear_gradient("L").resize((width, height)))
    return image


def encode(image, fmt, **params):
    out = BytesIO()
    image.save(out, fmt, **params)
    return out.getvalue()


def image_value(image, fmt, content_type, filename, **params):
    return {
        "data": base64.b64encode(encode(image, fmt, **params)).decode("ascii"),
        "encoding": "base64",
        "content-type": content_type,
        "filename": filename,
    }


def png(filename="photo.png"):
    return image_value(noise_image(60, 40), "PNG", "image/png", filename)


def svg(filename="icon.svg"):
    return {
        "data": base64.b64encode(SVG).decode("ascii"),
        "encoding": "base64",
        "content-type": "image/svg+xml",
        "filename": filename,
    }


def card_block(image):
    return {
        "@type": "testo_riquadro_immagine",
        "image": image,
        "showImage": True,
        "image_card_title": "Card",
    }


def alert_block(image):
    return {"@type": "alert", "image": image, "color": "info"}


def images(container):
    return [obj for obj in container.objectValues() if obj.portal_type == "Image"]


def open_image(data):
    return Image.open(BytesIO(data))


class OptimizeImageTest(unittest.TestCase):
    def optimize(self, raw, content_type="image/jpeg", filename="image.jpg"):
        return optimize_image_with_stats(raw, content_type, filename)

    def test_big_png_with_alpha_is_converted_to_webp(self):
        raw = encode(noise_image(2400, 300, mode="RGBA"), "PNG")

        new_raw, stats = self.optimize(raw, "image/png", "big.png")

        self.assertLess(len(new_raw), len(raw))
        image = open_image(new_raw)
        self.assertEqual(image.format, "WEBP")
        self.assertEqual(image.size, (MAX_SIDE, 200))
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(stats["old_size"], (2400, 300))
        self.assertEqual(stats["new_size"], (MAX_SIDE, 200))
        self.assertEqual(stats["old_bytes"], len(raw))
        self.assertEqual(stats["new_bytes"], len(new_raw))

    def test_small_webp_image_is_unchanged(self):
        raw = encode(noise_image(800, 600), "WEBP", quality=80)

        self.assertEqual(self.optimize(raw, "image/webp"), (None, None))

    def test_small_jpeg_is_converted_without_resize(self):
        raw = encode(noise_image(800, 600), "JPEG", quality=95)

        new_raw, stats = self.optimize(raw)

        self.assertEqual(open_image(new_raw).size, (800, 600))

    def test_small_image_is_unchanged(self):
        raw = encode(Image.new("RGB", (800, 600), "red"), "JPEG")

        self.assertEqual(self.optimize(raw), (None, None))

    def test_optimized_image_is_not_processed_again(self):
        new_raw, stats = self.optimize(encode(noise_image(2000, 600), "JPEG"))

        self.assertIsNotNone(new_raw)
        self.assertEqual(self.optimize(new_raw, "image/webp"), (None, None))

    def test_exif_orientation_is_applied(self):
        exif = Image.Exif()
        exif[0x0112] = 6  # rotate 90 CW
        raw = encode(noise_image(2000, 1000), "JPEG", exif=exif)

        new_raw, stats = self.optimize(raw)

        self.assertEqual(open_image(new_raw).size, (800, MAX_SIDE))

    def test_svg_is_unchanged(self):
        self.assertEqual(self.optimize(SVG, "image/svg+xml"), (None, None))

    def test_invalid_data_does_not_raise(self):
        new_raw, stats = self.optimize(b"not an image", "image/png", "broken.png")

        self.assertIsNone(new_raw)
        self.assertEqual(stats["filename"], "broken.png")
        self.assertIn("error", stats)


class UpgradeStep3106Test(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.document = createContentInContainer(
            self.portal, "Document", checkConstraints=False, title="Page"
        )

    def set_blocks(self, obj, blocks):
        obj.blocks = blocks
        obj.blocks_layout = {"items": list(blocks)}
        obj.reindexObject()

    def run_upgrade(self):
        with self.assertLogs("design.plone.policy.upgrades", level="INFO") as logs:
            to_3106(None)
        return "\n".join(logs.output)

    def assert_converted(self, value, image, context):
        self.assertEqual(
            value,
            [
                {
                    "@id": f"{'../' * (len(context.getPhysicalPath()) - 2)}"
                    f"resolveuid/{image.UID()}",
                    "image_field": "image",
                }
            ],
        )

    def test_card_block_is_converted(self):
        value = png()
        self.set_blocks(
            self.document,
            {"card": card_block(value), "title": {"@type": "title"}},
        )

        output = self.run_upgrade()

        [image] = images(self.document)
        self.assertEqual(image.title, "photo")
        # a small image is stored as is
        self.assertEqual(image.image.filename, "photo.png")
        self.assertEqual(image.image.contentType, "image/png")
        self.assertEqual(image.image.data, base64.b64decode(value["data"]))
        block = self.document.blocks["card"]
        self.assert_converted(block["image"], image, self.document)
        self.assertEqual(block["image_card_title"], "Card")
        self.assertEqual(self.document.blocks["title"], {"@type": "title"})
        self.assertIn(
            f'/plone/page - testo_riquadro_immagine "photo.png" '
            f"{human_size(len(image.image.data))} -> /plone/page/{image.getId()}",
            output,
        )
        self.assertIn("Modified pages: 1", output)
        self.assertIn("Created images: 1", output)
        self.assertIn("Optimized images: 0", output)
        self.assertIn("Images not converted for errors: 0", output)

    def test_big_image_is_optimized_before_conversion(self):
        value = image_value(
            noise_image(2400, 300, mode="RGBA"),
            "PNG",
            "image/png",
            "https://www.example.org/05_digitalizzazione_.png",
        )
        self.set_blocks(self.document, {"card": card_block(value)})

        output = self.run_upgrade()

        [image] = images(self.document)
        self.assertEqual(image.title, "05_digitalizzazione_")
        self.assertEqual(image.image.filename, "05_digitalizzazione_.webp")
        self.assertEqual(image.image.contentType, "image/webp")
        self.assertEqual(image.image.getImageSize(), (MAX_SIDE, 200))
        stored = open_image(image.image.data)
        self.assertEqual(stored.format, "WEBP")
        self.assertEqual(stored.mode, "RGBA")
        self.assertLess(image.image.getSize(), len(base64.b64decode(value["data"])))
        self.assert_converted(
            self.document.blocks["card"]["image"], image, self.document
        )
        self.assertIn(
            "/plone/page - optimized testo_riquadro_immagine "
            '"https://www.example.org/05_digitalizzazione_.png" image/png 2400x300',
            output,
        )
        self.assertIn("Created images: 1", output)
        self.assertIn("Optimized images: 1", output)

    def test_already_optimized_webp_is_not_encoded_again(self):
        value = image_value(
            noise_image(1600, 400), "WEBP", "image/webp", "optimized.webp"
        )
        self.set_blocks(self.document, {"alert": alert_block(value)})

        output = self.run_upgrade()

        [image] = images(self.document)
        self.assertEqual(image.image.data, base64.b64decode(value["data"]))
        self.assertEqual(image.image.filename, "optimized.webp")
        self.assertIn("Optimized images: 0", output)

    def test_not_an_image_is_stored_as_is(self):
        value = {
            "data": base64.b64encode(b"not an image").decode("ascii"),
            "encoding": "base64",
            "content-type": "image/png",
            "filename": "weird.png",
        }
        self.set_blocks(self.document, {"card": card_block(value)})

        output = self.run_upgrade()

        [image] = images(self.document)
        self.assertEqual(image.image.data, b"not an image")
        self.assertIn(
            '/plone/page - testo_riquadro_immagine "weird.png" '
            "not optimized, stored as is:",
            output,
        )
        self.assertIn("Created images: 1", output)
        self.assertIn("Optimized images: 0", output)

    def test_nested_alert_block_is_converted(self):
        self.set_blocks(
            self.document,
            {
                "grid": {
                    "@type": "gridBlock",
                    "blocks": {"alert": alert_block(png("alert.png"))},
                    "blocks_layout": {"items": ["alert"]},
                }
            },
        )

        self.run_upgrade()

        [image] = images(self.document)
        self.assertEqual(image.title, "alert")
        self.assert_converted(
            self.document.blocks["grid"]["blocks"]["alert"]["image"],
            image,
            self.document,
        )

    def test_svg_and_filename_url_are_converted(self):
        self.set_blocks(
            self.document,
            {
                "svg": card_block(svg()),
                "url": alert_block(png("https://www.example.org/img/remote.png")),
            },
        )

        self.run_upgrade()

        by_title = {image.title: image for image in images(self.document)}
        self.assertEqual(sorted(by_title), ["icon", "remote"])
        # SVG images are stored as is
        self.assertEqual(by_title["icon"].image.data, SVG)
        self.assertEqual(by_title["icon"].image.contentType, "image/svg+xml")
        self.assertEqual(by_title["remote"].image.filename, "remote.png")
        self.assert_converted(
            self.document.blocks["svg"]["image"], by_title["icon"], self.document
        )

    def test_blocks_field_is_converted(self):
        persona = createContentInContainer(
            self.portal, "Persona", checkConstraints=False, title="John Doe"
        )
        persona.competenze = {
            "blocks": {"alert": alert_block(png("alert.png"))},
            "blocks_layout": {"items": ["alert"]},
        }
        # set by collective.volto.blocksfield when a blocks field is saved
        alsoProvides(persona, IBlocksFieldEnabled)
        persona.reindexObject()

        self.run_upgrade()

        [image] = images(persona)
        self.assert_converted(
            persona.competenze["blocks"]["alert"]["image"], image, persona
        )

    def test_site_root_blocks_are_converted_in_root(self):
        existing = set(self.portal.objectIds())
        self.set_blocks(self.portal, {"card": card_block(png("home.png"))})

        self.run_upgrade()

        [new_id] = set(self.portal.objectIds()) - existing
        image = self.portal[new_id]
        self.assertEqual(image.portal_type, "Image")
        self.assertEqual(
            self.portal.blocks["card"]["image"],
            [{"@id": f"resolveuid/{image.UID()}", "image_field": "image"}],
        )

    def test_not_folderish_context_uses_parent(self):
        folder = createContentInContainer(
            self.portal, "Folder", checkConstraints=False, title="Folder"
        )
        link = createContentInContainer(
            folder, "Link", checkConstraints=False, title="Link"
        )
        blocks = {"card": card_block(png())}

        changes = convert_blocks(link, blocks)

        [image] = images(folder)
        self.assertEqual(changes[0]["path"], f"/plone/folder/{image.getId()}")
        self.assert_converted(blocks["card"]["image"], image, link)

    def test_upgrade_is_idempotent(self):
        self.set_blocks(self.document, {"card": card_block(png())})
        self.run_upgrade()
        blocks = self.document.blocks

        output = self.run_upgrade()

        self.assertEqual(len(images(self.document)), 1)
        self.assertEqual(self.document.blocks, blocks)
        self.assertIn("Modified pages: 0", output)
        self.assertIn("Created images: 0", output)

    def test_invalid_image_is_left_untouched(self):
        broken = {
            "data": "not an image",
            "encoding": "base64",
            "content-type": "image/png",
            "filename": "broken.png",
        }
        self.set_blocks(
            self.document,
            {"broken": card_block(broken), "card": card_block(png())},
        )
        other = createContentInContainer(
            self.portal, "Document", checkConstraints=False, title="Other"
        )
        self.set_blocks(other, {"alert": alert_block(png("other.png"))})

        output = self.run_upgrade()

        self.assertEqual(self.document.blocks["broken"]["image"], broken)
        self.assertEqual(len(images(self.document)), 1)
        self.assertEqual(len(images(other)), 1)
        self.assertIn(
            '/plone/page - testo_riquadro_immagine "broken.png" not converted:',
            output,
        )
        self.assertIn("Modified pages: 2", output)
        self.assertIn("Created images: 2", output)
        self.assertIn("Images not converted for errors: 1", output)
        self.assertIn('Not converted: /plone/page - "broken.png"', output)

    def test_only_broken_images_leave_page_untouched(self):
        broken = {
            "data": "",
            "encoding": "base64",
            "content-type": "image/png",
            "filename": "empty.png",
        }
        self.set_blocks(self.document, {"broken": card_block(broken)})
        blocks = self.document.blocks

        output = self.run_upgrade()

        self.assertIs(self.document.blocks, blocks)
        self.assertEqual(len(images(self.document)), 0)
        self.assertIn("Modified pages: 0", output)
        self.assertIn("Images not converted for errors: 1", output)

    def test_image_has_the_visibility_of_the_page(self):
        published = self.document
        private = createContentInContainer(
            self.portal, "Document", checkConstraints=False, title="Private"
        )
        api.content.transition(obj=published, transition="publish")
        self.set_blocks(published, {"card": card_block(png())})
        self.set_blocks(private, {"card": card_block(png())})

        self.run_upgrade()

        [published_image] = images(published)
        [private_image] = images(private)
        self.assertEqual(self.portal.portal_workflow.getChainFor(published_image), ())
        logout()
        self.assertTrue(api.user.has_permission("View", obj=published_image))
        self.assertFalse(api.user.has_permission("View", obj=private_image))


class UpgradeStep3106RestApiTest(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.document = createContentInContainer(
            self.portal, "Document", checkConstraints=False, title="Page"
        )
        self.document.blocks = {
            "card": card_block(png()),
            "alert": alert_block(png("alert.png")),
        }
        self.document.blocks_layout = {"items": ["card", "alert"]}
        self.document.reindexObject()
        with self.assertLogs("design.plone.policy.upgrades", level="INFO"):
            to_3106(None)
        commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_get_returns_image_url_and_scales(self):
        blocks = self.api_session.get("/page").json()["blocks"]

        [image] = blocks["card"]["image"]
        card_image = self.document[image["@id"].rsplit("/", 1)[-1]]
        self.assertEqual(image["@id"], f"{self.portal_url}/page/{card_image.getId()}")
        self.assertEqual(image["image_field"], "image")
        self.assertEqual(image["image_scales"]["image"][0]["width"], 60)
        self.assertIn("icon", image["image_scales"]["image"][0]["scales"])

    def test_restapi_save_stores_the_migrated_value(self):
        migrated = self.document.blocks["card"]["image"]
        [image] = self.api_session.get("/page").json()["blocks"]["card"]["image"]
        path = image["@id"][len(self.portal_url) :]
        blocks = {
            # what the frontend sends after picking or uploading the image
            "absolute": card_block([image]),
            "path": card_block([{"@id": path, "image_field": "image"}]),
        }

        response = self.api_session.patch(
            "/page",
            json={"blocks": blocks, "blocks_layout": {"items": list(blocks)}},
        )
        self.assertEqual(response.status_code, 204, response.text)
        commit()

        self.assertIn("image_scales", image)
        for name in ("absolute", "path"):
            self.assertEqual(self.document.blocks[name]["image"], migrated, name)

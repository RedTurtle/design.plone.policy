# -*- coding: utf-8 -*-
from collective.volto.blocksfield.interfaces import IBlocksFieldEnabled
from design.plone.policy.block_images import MAX_SIDE
from design.plone.policy.block_images import optimize_image
from design.plone.policy.block_images import optimize_image_with_stats
from design.plone.policy.testing import DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from design.plone.policy.upgrades import to_3105
from io import BytesIO
from PIL import Image
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


def noise_image(width, height, mode="RGB"):
    image = Image.merge(
        "RGB", [Image.effect_noise((width, height), 40) for _ in range(3)]
    )
    if mode == "RGBA":
        image.putalpha(Image.linear_gradient("L").resize((width, height)))
    return image


def image_value(image, fmt, content_type, filename, **params):
    out = BytesIO()
    image.save(out, fmt, **params)
    return {
        "data": base64.b64encode(out.getvalue()).decode("ascii"),
        "encoding": "base64",
        "content-type": content_type,
        "filename": filename,
    }


def big_jpeg(filename="photo.jpg"):
    return image_value(noise_image(2000, 600), "JPEG", "image/jpeg", filename)


def decode(value):
    return Image.open(BytesIO(base64.b64decode(value["data"])))


def card_block(image):
    return {
        "@type": "testo_riquadro_immagine",
        "image": image,
        "showImage": True,
        "image_card_title": "Card",
    }


class OptimizeImageTest(unittest.TestCase):
    def test_big_png_with_alpha_is_converted_to_webp(self):
        value = image_value(
            noise_image(2400, 300, mode="RGBA"),
            "PNG",
            "image/png",
            "https://www.example.org/05_digitalizzazione_.png",
        )

        result = optimize_image(value)

        self.assertEqual(result["content-type"], "image/webp")
        self.assertEqual(result["encoding"], "base64")
        self.assertEqual(
            result["filename"], "https://www.example.org/05_digitalizzazione_.webp"
        )
        self.assertLess(len(result["data"]), len(value["data"]))
        image = decode(result)
        self.assertEqual(image.format, "WEBP")
        self.assertEqual(image.size, (MAX_SIDE, 200))
        self.assertEqual(image.mode, "RGBA")

    def test_other_keys_are_kept(self):
        value = big_jpeg()
        value["extra"] = "foo"

        self.assertEqual(optimize_image(value)["extra"], "foo")

    def test_small_webp_image_is_unchanged(self):
        value = image_value(
            noise_image(800, 600), "WEBP", "image/webp", "small.webp", quality=80
        )

        self.assertIsNone(optimize_image(value))

    def test_small_jpeg_is_converted_without_resize(self):
        value = image_value(
            noise_image(800, 600), "JPEG", "image/jpeg", "small.jpg", quality=95
        )

        result = optimize_image(value)

        self.assertEqual(result["content-type"], "image/webp")
        self.assertEqual(decode(result).size, (800, 600))

    def test_small_image_is_unchanged(self):
        value = image_value(
            Image.new("RGB", (800, 600), "red"), "JPEG", "image/jpeg", "small.jpg"
        )

        self.assertIsNone(optimize_image(value))

    def test_optimized_image_is_not_processed_again(self):
        result = optimize_image(big_jpeg())

        self.assertIsNotNone(result)
        self.assertIsNone(optimize_image(result))

    def test_exif_orientation_is_applied(self):
        exif = Image.Exif()
        exif[0x0112] = 6  # rotate 90 CW
        value = image_value(
            noise_image(2000, 1000), "JPEG", "image/jpeg", "rotated.jpg", exif=exif
        )

        result = optimize_image(value)

        self.assertEqual(decode(result).size, (800, MAX_SIDE))

    def test_unsupported_values_are_ignored(self):
        self.assertIsNone(optimize_image(None))
        self.assertIsNone(optimize_image("foo"))
        self.assertIsNone(optimize_image({}))
        self.assertIsNone(optimize_image({"download": "http://example.org/x.png"}))
        self.assertIsNone(
            optimize_image(
                {
                    "data": base64.b64encode(b"<svg></svg>").decode("ascii"),
                    "encoding": "base64",
                    "content-type": "image/svg+xml",
                    "filename": "icon.svg",
                }
            )
        )

    def test_invalid_data_does_not_raise(self):
        value = {
            "data": "not an image",
            "encoding": "base64",
            "content-type": "image/png",
            "filename": "broken.png",
        }

        new_value, stats = optimize_image_with_stats(value)

        self.assertIsNone(new_value)
        self.assertIn("error", stats)


class BlockImagesDeserializerTest(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.document = createContentInContainer(
            self.portal, "Document", checkConstraints=False, title="Page"
        )
        commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def patch_blocks(self, path, blocks):
        response = self.api_session.patch(
            path,
            json={"blocks": blocks, "blocks_layout": {"items": list(blocks)}},
        )
        self.assertEqual(response.status_code, 204, response.text)
        return self.api_session.get(path).json()["blocks"]

    def test_images_are_optimized_on_save(self):
        blocks = {
            "card": card_block(big_jpeg("card.jpg")),
            "alert": {"@type": "alert", "image": big_jpeg("alert.jpg")},
            "grid": {
                "@type": "gridBlock",
                "blocks": {"nested": card_block(big_jpeg("nested.jpg"))},
                "blocks_layout": {"items": ["nested"]},
            },
            "title": {"@type": "title"},
        }

        result = self.patch_blocks("/page", blocks)

        for image in (
            result["card"]["image"],
            result["alert"]["image"],
            result["grid"]["blocks"]["nested"]["image"],
        ):
            self.assertEqual(image["content-type"], "image/webp")
            self.assertEqual(max(decode(image).size), MAX_SIDE)
        self.assertEqual(result["card"]["image"]["filename"], "card.webp")
        self.assertEqual(result["title"], blocks["title"])

    def test_save_again_does_not_change_image(self):
        result = self.patch_blocks("/page", {"card": card_block(big_jpeg())})

        again = self.patch_blocks("/page", result)

        self.assertEqual(again["card"]["image"], result["card"]["image"])

    def test_images_are_optimized_on_site_root(self):
        result = self.patch_blocks("", {"card": card_block(big_jpeg())})

        self.assertEqual(result["card"]["image"]["content-type"], "image/webp")


class BlockImagesUpgradeTest(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_upgrade_optimizes_existing_contents(self):
        document = createContentInContainer(
            self.portal, "Document", checkConstraints=False, title="Page"
        )
        document.blocks = {
            "card": card_block(big_jpeg("card.jpg")),
            "small": card_block(
                image_value(noise_image(100, 100), "WEBP", "image/webp", "small.webp")
            ),
        }
        document.reindexObject()
        persona = createContentInContainer(
            self.portal, "Persona", checkConstraints=False, title="John Doe"
        )
        persona.competenze = {
            "blocks": {"alert": {"@type": "alert", "image": big_jpeg("alert.jpg")}},
            "blocks_layout": {"items": ["alert"]},
        }
        # set by collective.volto.blocksfield when a blocks field is saved
        alsoProvides(persona, IBlocksFieldEnabled)
        persona.reindexObject()

        with self.assertLogs("design.plone.policy.upgrades", level="INFO") as logs:
            to_3105(None)

        self.assertEqual(document.blocks["card"]["image"]["content-type"], "image/webp")
        self.assertEqual(document.blocks["small"]["image"]["filename"], "small.webp")
        self.assertEqual(
            persona.competenze["blocks"]["alert"]["image"]["content-type"],
            "image/webp",
        )
        output = "\n".join(logs.output)
        self.assertIn(
            '/plone/page - testo_riquadro_immagine "card.jpg" image/jpeg', output
        )
        self.assertIn('/plone/john-doe - alert "alert.jpg" image/jpeg', output)
        self.assertIn("Modified pages: 2", output)
        self.assertIn("Optimized images: 2", output)
        self.assertIn("Total size:", output)

# -*- coding: utf-8 -*-
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from design.plone.policy.tests.test_upgrade_step_3106 import card_block
from design.plone.policy.tests.test_upgrade_step_3106 import image_value
from design.plone.policy.tests.test_upgrade_step_3106 import images
from design.plone.policy.tests.test_upgrade_step_3106 import noise_image
from design.plone.policy.upgrades.v3105 import to_3105
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer

import unittest


class UpgradeStep3105Test(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_upgrade_does_nothing(self):
        document = createContentInContainer(
            self.portal, "Document", checkConstraints=False, title="Page"
        )
        value = image_value(noise_image(2000, 600), "JPEG", "image/jpeg", "big.jpg")
        document.blocks = {"card": card_block(value)}
        document.blocks_layout = {"items": ["card"]}
        document.reindexObject()

        with self.assertLogs("design.plone.policy.upgrades", level="INFO") as logs:
            to_3105(None)

        self.assertEqual(document.blocks, {"card": card_block(value)})
        self.assertEqual(images(document), [])
        self.assertIn("3105 - 3106 upgrade step", "\n".join(logs.output))

# -*- coding: utf-8 -*-
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestInitialStructureCreation(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_plone_base_interfaces_syndication_ISiteSyndicationSettings_show_author_info(  # noqa
        self,
    ):
        self.assertFalse(
            api.portal.get_registry_record(
                "plone.base.interfaces.syndication.ISiteSyndicationSettings.show_author_info"  # noqa
            )
        )

# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from design.plone.policy.testing import (
    DESIGN_PLONE_POLICY_LIMIT_ROOT_ADDABLES_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.interfaces.controlpanel import INavigationSchema
from zope.component import getUtility

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that design.plone.policy is properly installed."""

    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_browserlayer(self):
        """Test that IDesignPlonePolicyLayer is registered."""
        from design.plone.policy.interfaces import IDesignPlonePolicyLayer
        from plone.browserlayer import utils

        self.assertIn(IDesignPlonePolicyLayer, utils.registered_layers())

    def test_show_excluded_items_disabled(self):
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(
            INavigationSchema, prefix="plone", check=False
        )
        self.assertFalse(navigation_settings.show_excluded_items)

    def test_sitemap_enabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        self.assertTrue(settings.enable_sitemap)

    def test_searchable_types(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSchema, prefix="plone")
        self.assertEqual(
            sorted(settings.types_not_searched),
            sorted(
                (
                    "File",
                    "Image",
                    "Incarico",
                    "Modulo",
                    "Documento Personale",
                    "Bando Folder Deepening",
                    "Pratica",
                    "TempFolder",
                    "Collection",
                    "RicevutaPagamento",
                    "Link",
                    "Messaggio",
                    "Plone Site",
                    "Folder",
                    "Dataset",
                    "Discussion Item",
                    "Subsite",
                )
            ),
        )


class TestUninstall(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("design.plone.policy")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if design.plone.policy is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("design.plone.policy"))

    def test_browserlayer_removed(self):
        """Test that IDesignPlonePolicyLayer is removed."""
        from design.plone.policy.interfaces import IDesignPlonePolicyLayer
        from plone.browserlayer import utils

        self.assertNotIn(IDesignPlonePolicyLayer, utils.registered_layers())


class TestSetupLimitRootAddables(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_LIMIT_ROOT_ADDABLES_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        self.installer.install_product("design.plone.policy.limit_root_addables")

    def test_setup(self):
        plonesite = api.portal.get_tool("portal_types")["Plone Site"]
        self.assertTrue(plonesite.filter_content_types)
        self.assertEqual(
            sorted(plonesite.allowed_content_types),
            sorted(("Folder", "File", "Document", "Image", "Subsite")),
        )


class TestUninstallLimitRootAddables(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        # roles_before = api.user.get_roles(TEST_USER_ID)
        # setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.install_product("design.plone.policy.limit_root_addables")
        # setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_uninstall(self):
        plonesite = api.portal.get_tool("portal_types")["Plone Site"]
        self.installer.uninstall_product("design.plone.policy.limit_root_addables")
        self.assertFalse(plonesite.filter_content_types)
        self.assertEqual(
            plonesite.allowed_content_types,
            (),
        )

# -*- coding: utf-8 -*-
from design.plone.policy.utils import folderSubstructureGenerator
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return ["design.plone.policy:uninstall"]


def post_install(context):
    """Post install script"""
    folderSubstructureGenerator("Amministrazione")
    folderSubstructureGenerator("Servizi")
    folderSubstructureGenerator("Novità")
    folderSubstructureGenerator("Documenti e dati")


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

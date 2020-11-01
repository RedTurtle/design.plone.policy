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
    folderSubstructureGenerator(
        title="Amministrazione", types=("Document", "Image", "File", "Link")
    )
    folderSubstructureGenerator(
        title="Servizi", types=("Document", "Image", "File", "Link")
    )
    folderSubstructureGenerator(
        title="Novità", types=("Document", "Image", "File", "Link")
    )
    folderSubstructureGenerator(
        title="Documenti e dati",
        types=(
            "Document",
            "Image",
            "File",
            "Link",
            "Documento",
            "CartellaModulistica",
        ),
    )
    folderSubstructureGenerator(
        title="Argomenti", types=("Document", "Image", "File", "Link")
    )


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

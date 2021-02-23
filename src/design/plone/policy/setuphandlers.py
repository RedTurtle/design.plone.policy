# -*- coding: utf-8 -*-
from design.plone.contenttypes.controlpanels.vocabularies import (
    IVocabulariesControlPanel,
)
from design.plone.policy.utils import folderSubstructureGenerator
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import json


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

    # set default search folders
    section_ids = ["amministrazione", "servizi", "novita", "documenti-e-dati"]
    sections = []
    portal = api.portal.get()
    for id in section_ids:
        item = portal.get(id, None)
        if item:
            sections.append({"title": item.title, "linkUrl": [item.UID()]})
    settings = [{"rootPath": "/", "items": sections}]
    api.portal.set_registry_record(
        "search_sections",
        json.dumps(settings),
        interface=IVocabulariesControlPanel,
    )


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

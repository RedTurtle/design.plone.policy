# -*- coding: utf-8 -*-
from design.plone.contenttypes.controlpanels.settings import (
    IDesignPloneSettings,
)
from design.plone.policy.utils import folderSubstructureGenerator
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces import ISearchSchema
from zope.component import getUtility
from zope.interface import implementer

import json


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "design.plone.policy:uninstall",
            "design.plone.policy:test",
            "design.plone.policy:to_1400",
        ]


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
            "Bando",
            "CartellaModulistica",
            "Document",
            "Documento",
            "File",
            "Image",
            "Link",
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
        interface=IDesignPloneSettings,
    )

    disable_searchable_types()


def disable_searchable_types():
    # remove some types from search enabled ones
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISearchSchema, prefix="plone")
    remove_types = [
        "Folder",
        "Bando Folder Deepening",
        "Link",
        "Collection",
        "Discussion Item",
        "Dataset",
        "Documento Personale",
        "Messaggio",
        "Pratica",
        "RicevutaPagamento",
    ]
    types = set(settings.types_not_searched)
    types.update(remove_types)
    settings.types_not_searched = tuple(types)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

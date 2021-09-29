# -*- coding: utf-8 -*-
from collective.volto.subsites.interfaces import IVoltoSubsitesSettings
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
    folderSubstructureGenerator(title="Amministrazione")
    folderSubstructureGenerator(title="Servizi")
    folderSubstructureGenerator(title="Novità")
    folderSubstructureGenerator(title="Documenti e dati")
    folderSubstructureGenerator(title="Argomenti")

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
    set_default_subsite_colors()


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


def set_default_subsite_colors():
    colors = [
        "white",
        "yellow",
        "magenta",
        "teal",
        "light-yellow",
        "light-pink",
        "light-teal",
        "light-blue",
    ]
    old = api.portal.get_registry_record(
        "available_styles", interface=IVoltoSubsitesSettings, default=[]
    )

    for color in colors:
        if color not in old:
            old.append(color)

    api.portal.set_registry_record(
        "available_styles", sorted(old), interface=IVoltoSubsitesSettings
    )


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

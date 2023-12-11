# -*- coding: utf-8 -*-
from collective.volto.subsites.interfaces import IVoltoSubsitesSettings
from design.plone.contenttypes.controlpanels.settings import IDesignPloneSettings
from design.plone.policy.utils import create_footer
from design.plone.policy.utils import create_menu
from design.plone.policy.utils import create_secondary_menu
from design.plone.policy.utils import folderSubstructureGenerator
from design.plone.policy.utils import TASSONOMIA_PRIMO_LIVELLO
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
    for x in TASSONOMIA_PRIMO_LIVELLO:
        types = []
        if x == "Argomenti":
            types = ["Pagina Argomento"]
            folderSubstructureGenerator(title="Argomenti", types=types)
        else:
            folderSubstructureGenerator(
                title=x,
            )

    # set default search folders
    section_ids = ["amministrazione", "servizi", "novita", "vivere-il-comune"]
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
    create_footer()
    create_menu()
    create_secondary_menu()


def disable_searchable_types(context=None):
    # remove some types from search enabled ones

    # This is the list updated at 2023/12/01 with all types that
    # could not be searchable in io-Comune

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
        "File",
        "Image",
        "Incarico",
        "Messaggio",
        "Modulo",
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

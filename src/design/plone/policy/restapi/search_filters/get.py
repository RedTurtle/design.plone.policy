# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from design.plone.contenttypes.controlpanels.settings import (
    IDesignPloneSettings,
)
from plone import api
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import ISearchSchema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import json


@implementer(IPublishTraverse)
class SearchFiltersGet(Service):
    def __init__(self, context, request):
        super(SearchFiltersGet, self).__init__(context, request)

    def get_basic_data(self, item):
        import pdb

        pdb.set_trace()
        return {
            "@id": item.getURL(),
            "title": item.Title,
            "description": item.description,
            "@type": item.portal_type,
            "path": item.getPath(),
            "UID": item.UID,
        }

    def get_portal_types(self):
        ttool = api.portal.get_tool("portal_types")
        ptool = api.portal.get_tool("plone_utils")
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        types_not_searched = search_settings.types_not_searched
        types = [
            {
                "label": translate(ttool[t].Title(), context=self.request),
                "id": t,
            }
            for t in ptool.getUserFriendlyTypes()
            if t not in types_not_searched
        ]
        return sorted(types, key=lambda k: k["label"])

    def reply(self):
        settings = api.portal.get_registry_record(
            "search_sections",
            interface=IDesignPloneSettings,
        )
        sections = []
        if settings:
            settings = json.loads(settings)
            for setting in settings:
                items = []
                for section_settings in setting.get("items", []):
                    for uid in section_settings.get("linkUrl", []):
                        try:
                            section = api.content.get(UID=uid)
                        except Unauthorized:
                            # private folder
                            continue
                        if section:
                            item_infos = getMultiAdapter(
                                (section, self.request),
                                ISerializeToJsonSummary,
                            )()
                            children = section.listFolderContents()
                            if children:
                                item_infos["items"] = []
                                for children in section.listFolderContents():
                                    item_infos["items"].append(
                                        getMultiAdapter(
                                            (children, self.request),
                                            ISerializeToJsonSummary,
                                        )()
                                    )
                            if section_settings.get("title", ""):
                                item_infos["title"] = section_settings["title"]
                            items.append(item_infos)
                if items:
                    sections.append(
                        {
                            "rootPath": setting.get("rootPath", ""),
                            "items": items,
                        }
                    )
        topics = [
            getMultiAdapter(
                (brain, self.request),
                ISerializeToJsonSummary,
            )()
            for brain in api.content.find(portal_type="Pagina Argomento")
        ]
        return {
            "sections": sections,
            "topics": topics,
            "portal_types": self.get_portal_types(),
        }

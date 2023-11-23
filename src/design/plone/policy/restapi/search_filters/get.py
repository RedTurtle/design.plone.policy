# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from design.plone.contenttypes.controlpanels.settings import IDesignPloneSettings
from plone import api
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFCore.utils import getToolByName
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
            "search_sections", interface=IDesignPloneSettings, default="[]"
        )
        utils = getToolByName(self.context, "plone_utils")

        sections = []
        for setting in json.loads(settings or "[]"):
            items = []
            for section_settings in setting.get("items") or []:
                for uid in section_settings.get("linkUrl") or []:
                    try:
                        section = api.content.get(UID=uid)
                    except Unauthorized:
                        # private folder
                        continue
                    if not section:
                        continue
                    item_infos = getMultiAdapter(
                        (section, self.request),
                        ISerializeToJsonSummary,
                    )()
                    children = section.listFolderContents(
                        contentFilter={"portal_type": utils.getUserFriendlyTypes()}
                    )
                    item_infos["items"] = [
                        getMultiAdapter(
                            (x, self.request),
                            ISerializeToJsonSummary,
                        )()
                        for x in children
                    ]
                    item_infos["title"] = section_settings.get("title", "")
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
            for brain in api.content.find(
                portal_type="Pagina Argomento",
                sort_on="sortable_title",
                sort_order="ascending",
            )
        ]
        return {
            "sections": sections,
            "topics": topics,
            "portal_types": self.get_portal_types(),
        }

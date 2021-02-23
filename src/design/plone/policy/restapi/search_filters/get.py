# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from design.plone.contenttypes.controlpanels.vocabularies import (
    IVocabulariesControlPanel,
)
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone import api
from zope.component import getMultiAdapter

import json


@implementer(IPublishTraverse)
class SearchFiltersGet(Service):
    def __init__(self, context, request):
        super(SearchFiltersGet, self).__init__(context, request)

    def get_basic_data(self, item):
        return {
            "@id": item.absolute_url(),
            "title": item.Title(),
            "description": item.description,
            "@type": item.portal_type,
            "path": item.virtual_url_path(),
            "UID": item.UID(),
        }

    def reply(self):
        settings = api.portal.get_registry_record(
            "search_sections", interface=IVocabulariesControlPanel,
        )
        sections = []
        topics = []
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
                                        self.get_basic_data(item=children)
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
        for argument in api.content.find(portal_type="Pagina Argomento"):
            topics.append(self.get_basic_data(argument.getObject()))
        return {"sections": sections, "topics": topics}

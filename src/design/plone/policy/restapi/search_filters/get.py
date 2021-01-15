# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone import api

SECTION_IDS = ["amministrazione", "servizi", "novita", "documenti-e-dati"]


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
        portal_path = "/".join(api.portal.get().getPhysicalPath())
        sections = {}
        topics = []

        for section_id in SECTION_IDS:
            section_path = "{portal}/{id}".format(
                portal=portal_path, id=section_id
            )
            try:
                section = api.content.get(section_path)
            except Unauthorized:
                # private folder
                continue
            if not section:
                continue
            sections[section_id] = self.get_basic_data(item=section)
            sections[section_id]["items"] = []
            for children in section.listFolderContents():
                sections[section_id]["items"].append(
                    self.get_basic_data(item=children)
                )
        for argument in api.content.find(portal_type="Pagina Argomento"):
            topics.append(self.get_basic_data(argument.getObject()))
        res = {"sections": sections, "topics": topics}
        return res

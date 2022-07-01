# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class BandiSearchFiltersGet(Service):
    def reply(self):
        subjects = [
            {"UID": x, "title": x}
            for x in self.context.portal_catalog.uniqueValuesFor("Subject_bando")
        ]

        uffici_uids = self.context.portal_catalog.uniqueValuesFor(
            "ufficio_responsabile_bando"
        )
        offices = [
            {"UID": x.UID, "title": x.Title} for x in api.content.find(UID=uffici_uids)
        ]

        subjects.sort(key=lambda x: x["title"])
        offices.sort(key=lambda x: x["title"])
        return {
            "subjects": subjects,
            "offices": offices,
        }

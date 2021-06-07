# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class BandiSearchFiltersGet(Service):
    def reply(self):
        subjects = []
        offices = []

        for brain in api.content.find(portal_type="Bando"):
            bando = brain.getObject()
            for subject in getattr(bando, "subject", []):
                if subject not in subjects:
                    subjects.append({"UID": subject, "title": subject})
            for rel in getattr(bando, "ufficio_responsabile", []):
                uo = rel.to_object
                if uo:
                    if api.user.has_permission("View", obj=uo):
                        uo_data = {"UID": uo.UID(), "title": uo.Title()}
                        if uo_data not in offices:
                            offices.append(uo_data)
        subjects.sort(key=lambda x: x["title"])
        offices.sort(key=lambda x: x["title"])

        return {
            "subjects": subjects,
            "offices": offices,
        }

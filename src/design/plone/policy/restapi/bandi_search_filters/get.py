# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class BandiSearchFiltersGet(Service):
    def reply(self):
        subjects_keys = []
        offices_keys = []
        subjects = []
        offices = []

        # populate with only list from visible bandi
        for brain in api.content.find(portal_type="Bando"):
            for subject in brain.Subject_bando or []:
                if subject in subjects_keys:
                    continue
                subjects_keys.append(subject)
                subjects.append({"UID": subject, "title": subject})
            for uid in brain.ufficio_responsabile_bando or []:
                if uid in offices_keys:
                    continue
                # add also if it's private, so we will not check it anymore
                offices_keys.append(uid)
                try:
                    item = api.content.get(UID=uid)
                except Unauthorized:
                    continue
                if item:
                    offices.append({"UID": uid, "title": item.Title()})
        offices.sort(key=lambda x: x["title"])
        subjects.sort(key=lambda x: x["title"])

        return {
            "subjects": subjects,
            "offices": offices,
        }

# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class BandiSearchFiltersGet(Service):
    def reply(self):
        """
        Return possible values based also on current user permissions
        """
        subjects = []
        pc = api.portal.get_tool(name="portal_catalog")
        for subject in pc.uniqueValuesFor("Subject_bando"):
            res = api.content.find(Subject_bando=subject)
            if res:
                subjects.append({"UID": subject, "title": subject})

        office_uids = pc.uniqueValuesFor("ufficio_responsabile_bando")
        offices = [{"UID": x.UID, "title": x.Title} for x in pc(UID=office_uids)]

        subjects.sort(key=lambda x: x["title"])
        offices.sort(key=lambda x: x["title"])
        return {
            "subjects": subjects,
            "offices": offices,
        }

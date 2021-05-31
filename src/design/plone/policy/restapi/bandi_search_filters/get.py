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
class BandiSearchFiltersGet(Service):
    def reply(self):
        subjects = []
        offices = []

        for brain in api.content.find(portal_type="Bando"):
            bando = brain.getObject()
            for subject in getattr(bando, "subject", []):
                if subject not in subjects:
                    subjects.append(subject)
            for rel in getattr(bando, "ufficio_responsabile", []):
                uo = rel.to_object
                if uo:
                    if api.user.has_permission("View", obj=uo):
                        uo_data = {"key": uo.UID(), "label": uo.Title()}
                        if uo_data not in offices:
                            offices.append(uo_data)
        subjects.sort()
        offices.sort(key=lambda x: x["label"])

        return {
            "subjects": subjects,
            "offices": offices,
        }

# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.restapi.services import Service
from redturtle.bandi.vocabularies import TipologiaBandoVocabularyFactory
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class BandiSearchFiltersGet(Service):
    def reply(self):
        """
        Return possible values based also on current user permissions
        """
        pc = api.portal.get_tool(name="portal_catalog")
        voc_tipologie = TipologiaBandoVocabularyFactory(self.context)

        tipologie = []
        subjects = []
        offices = []

        bandi_folder = None

        if IDexterityContainer.providedBy(self.context):
            bandi_folder = self.context

        if bandi_folder:
            bandi_folder_path = "/".join(bandi_folder.getPhysicalPath())
            query = {"portal_type": ["Bando"], "path": bandi_folder_path}
            brains = pc(query)

            for brain in brains:
                bando = brain.getObject()
                found = [x for x in tipologie if x["UID"] == bando.tipologia_bando]
                if not found:
                    tipologie.append(
                        {
                            "UID": bando.tipologia_bando,
                            "title": voc_tipologie.getTerm(bando.tipologia_bando).title,
                        }
                    )
                for sub in bando.subject:
                    found = [x for x in subjects if x["UID"] == sub]
                    if not found:
                        subjects.append({"UID": sub, "title": sub})

                for office_relation in bando.ufficio_responsabile:
                    offices.append(
                        {
                            "UID": office_relation.to_object.UID(),
                            "title": office_relation.to_object.title,
                        }
                    )
        else:
            for subject in pc.uniqueValuesFor("Subject_bando"):
                res = api.content.find(Subject_bando=subject)
                if res:
                    subjects.append({"UID": subject, "title": subject})

            for item in voc_tipologie.by_token:
                tipologie.append(
                    {"UID": item, "title": voc_tipologie.getTerm(item).title}
                )

            office_uids = pc.uniqueValuesFor("ufficio_responsabile_bando")
            offices = [{"UID": x.UID, "title": x.Title} for x in pc(UID=office_uids)]

        subjects.sort(key=lambda x: x["title"])
        offices.sort(key=lambda x: x["title"])
        tipologie.sort(key=lambda x: x["title"])
        return {
            "subjects": subjects,
            "offices": offices,
            "tipologie": tipologie,
        }

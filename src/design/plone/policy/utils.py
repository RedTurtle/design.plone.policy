# -*- coding: utf-8 -*-
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.component import getUtility


TASSONOMIA_SERVIZI = [
    "Anagrafe e stato civile",
    "Cultura e tempo libero",
    "Vita lavorativa",
    "Attività produttive e commercio",
    "Appalti pubblici",
    "Catasto e urbanistica",
    "Turismo",
    "Mobilità e trasporti",
    "Educazione e formazione",
    "Giustizia e sicurezza pubblica",
    "Tributi e finanze",
    "Ambiente",
    "Salute, benessere e assistenza",
    "Autorizzazioni",
    "Agricoltura",
]

TASSONOMIA_DOCUMENTI = [
    "Documenti albo pretorio",
    "Modulistica",
    "Documenti funzionamento interno",
    "Atti normativi",
    "Accordi tra enti",
    "Documenti attività politica",
    "Documenti (tecnici) di supporto",
    "Istanze",
    "Dataset",
]

TASSONOMIA_NEWS = ["Notizie", "Comunicati", "Eventi"]
TASSONOMIA_AMMINISTRAZIONE = [
    "Politici",
    "Personale Amministrativo",
    "Organi di governo",
    "Aree amministrative",
    "Uffici",
    "Enti e fondazioni",
    "Luoghi",
]


def folderSubstructureGenerator(title, types=[]):
    container = api.portal.get()

    normalizer = getUtility(IIDNormalizer)
    safe_id = normalizer.normalize(title)

    root_path = "/".join(container.getPhysicalPath())
    path = root_path + "/" + safe_id

    if api.content.get(path=path):
        return

    tree_root = api.content.create(container=container, type="Document", title=title)
    api.content.transition(obj=tree_root, transition="publish")
    if types:
        restrict_types(context=tree_root, types=types)

    if title == "Servizi":
        for ts in TASSONOMIA_SERVIZI:
            api.content.create(container=tree_root, type="Document", title=ts)

    elif title == "Documenti e dati":
        for td in TASSONOMIA_DOCUMENTI:
            api.content.create(container=tree_root, type="Document", title=td)

    elif title == "Novità":
        for tn in TASSONOMIA_NEWS:
            api.content.create(container=tree_root, type="Document", title=tn)

    elif title == "Amministrazione":
        for ta in TASSONOMIA_AMMINISTRAZIONE:
            api.content.create(container=tree_root, type="Document", title=ta)


def restrict_types(context, types):
    constraints = ISelectableConstrainTypes(context)
    constraints.setConstrainTypesMode(1)
    constraints.setLocallyAllowedTypes(types)

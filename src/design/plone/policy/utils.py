# -*- coding: utf-8 -*-
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.component import getUtility
from uuid import uuid4

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
    create_default_blocks(context=tree_root)

    api.content.transition(obj=tree_root, transition="publish")
    if types:
        restrict_types(context=tree_root, types=types)

    if title == "Servizi":
        for ts in TASSONOMIA_SERVIZI:
            child = api.content.create(container=tree_root, type="Document", title=ts)
            create_default_blocks(context=child)
    elif title == "Documenti e dati":
        for td in TASSONOMIA_DOCUMENTI:
            child = api.content.create(container=tree_root, type="Document", title=td)
            create_default_blocks(context=child)

    elif title == "Novità":
        for tn in TASSONOMIA_NEWS:
            child = api.content.create(container=tree_root, type="Document", title=tn)
            create_default_blocks(context=child)

    elif title == "Amministrazione":
        for ta in TASSONOMIA_AMMINISTRAZIONE:
            child = api.content.create(container=tree_root, type="Document", title=ta)
            create_default_blocks(context=child)


def restrict_types(context, types):
    constraints = ISelectableConstrainTypes(context)
    constraints.setConstrainTypesMode(1)
    constraints.setLocallyAllowedTypes(types)


def create_default_blocks(context):
    title_uuid = str(uuid4())
    context.blocks = {title_uuid: {"@type": "title"}}
    context.blocks_layout = {"items": [title_uuid]}

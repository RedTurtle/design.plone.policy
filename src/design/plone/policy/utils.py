# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from collective.volto.secondarymenu.interfaces import ISecondaryMenu
from collective.volto.subfooter.interfaces import ISubfooter
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from redturtle.voltoplugin.editablefooter.interfaces import IEditableFooterSettings
from uuid import uuid4
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest

import json
import time


TASSONOMIA_PRIMO_LIVELLO = [
    "Amministrazione",
    "Novità",
    "Servizi",
    "Vivere il Comune",
    "Argomenti",
]

TASSONOMIA_SERVIZI = [
    "Educazione e formazione",
    "Salute, benessere e assistenza",
    "Vita lavorativa",
    "Mobilità e trasporti",
    "Catasto e urbanistica",
    "Anagrafe e stato civile",
    "Turismo",
    "Giustizia e sicurezza pubblica",
    "Tributi, finanze e contravvenzioni",
    "Cultura e tempo libero",
    "Ambiente",
    "Imprese e commercio",
    "Autorizzazioni",
    "Appalti pubblici",
    "Agricoltura e pesca",
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
    "Documenti di programmazione e rendicontazione",
    "Dataset",
]

TASSONOMIA_NEWS = ["Notizie", "Comunicati", "Avvisi"]
TASSONOMIA_AMMINISTRAZIONE = [
    "Organi di governo",
    "Aree amministrative",
    "Uffici",
    "Enti e fondazioni",
    "Politici",
    "Personale Amministrativo",
    "Documenti e dati",
]

TASSONOMIA_VIVERE_IL_COMUNE = ["Luoghi", "Eventi"]

TASSONOMIA_ORGANI_GOVERNO = [
    "Giunta comunale",
    "Consiglio comunale",
    "Commissione",
]

TASSONOMIA_ARGOMENTI = [
    "Accesso all'informazione",
    "Acqua",
    "Agricoltura",
    "Animale domestico",
    "Aria",
    "Assistenza agli invalidi",
    "Assistenza sociale",
    "Associazioni",
    "Bilancio",
    "Commercio all'ingrosso",
    "Commercio al minuto",
    "Commercio ambulante",
    "Comunicazione istituzionale",
    "Comunicazione politica",
    "Concorsi",
    "Covid-19",
    "Elezioni",
    "Energie rinnovabili",
    "Estero",
    "Foreste",
    "Formazione professionale",
    "Gemellaggi",
    "Gestione rifiuti",
    "Giustizia",
    "Igiene pubblica",
    "Immigrazione",
    "Imposte",
    "Imprese",
    "Inquinamento",
    "Integrazione sociale",
    "Isolamento termico",
    "Istruzione",
    "Lavoro",
    "Matrimonio",
    "Mercato",
    "Mobilità sostenibile",
    "Morte",
    "Nascita",
    "Parcheggi",
    "Patrimonio culturale",
    "Pesca",
    "Piano di sviluppo",
    "Pista ciclabile",
    "Politica commerciale",
    "Polizia",
    "Prodotti alimentari",
    "Protezione civile",
    "Residenza",
    "Risposta alle emergenze",
    "Sistema giuridico",
    "Spazio Verde",
    "Sport",
    "Sviluppo sostenibile",
    "Tassa sui servizi",
    "Tempo libero",
    "Trasparenza amministrativa",
    "Trasporto pubblico",
    "Turismo",
    "Urbanizzazione",
    "Viaggi",
    "Zone pedonali",
    "ZTL",
]

TASSONOMIA_FOOTER = [
    {"title": "Leggi le FAQ", "type": "FaqFolder", "data-element": "faq"},
    {
        "title": "Prenotazione appuntamento",
        "type": "Document",
        "data-element": "appointment-booking",
    },
    {
        "title": "Segnalazione disservizio",
        "type": "Document",
        "data-element": "report-inefficiency",
    },
    {"title": "Richiesta di assistenza", "type": "Document"},
    {"title": "Amministrazione trasparente", "type": "Document"},
    {
        "title": "Informativa privacy",
        "type": "Document",
        "data-element": "privacy-policy-link",
    },
    {"title": "Note legali", "type": "Document"},
    {
        "title": "Dichiarazione di accessibilità",
        "type": "Link",
        "data-element": "accessibility-link",
    },
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
    elif title == "Vivere il Comune":
        for td in TASSONOMIA_VIVERE_IL_COMUNE:
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
            if ta == "Documenti e dati":
                for tdd in TASSONOMIA_DOCUMENTI:
                    grandchild = api.content.create(
                        container=child, type="Document", title=tdd
                    )
                    create_default_blocks(context=grandchild)
            elif ta == "Organi di governo":
                for tog in TASSONOMIA_ORGANI_GOVERNO:
                    grandchild = api.content.create(
                        container=child, type="Document", title=tog
                    )
                    create_default_blocks(context=grandchild)

    elif title == "Argomenti":
        for ta in TASSONOMIA_ARGOMENTI:
            child = api.content.create(
                container=tree_root, type="Pagina Argomento", title=ta
            )
            create_default_blocks(context=child)


def restrict_types(context, types):
    constraints = ISelectableConstrainTypes(context)
    constraints.setConstrainTypesMode(1)
    constraints.setLocallyAllowedTypes(types)


def create_default_blocks(context):
    if IBlocks.providedBy(context):
        title_uuid = str(uuid4())
        context.blocks = {title_uuid: {"@type": "title"}}
        context.blocks_layout = {"items": [title_uuid]}


def create_footer():
    container = api.portal.get()
    # Generate needed pages
    for item in TASSONOMIA_FOOTER:
        obj = api.content.create(
            container=container,
            type=item.get("type", "Pagina"),
            title=item.get("title", "Titolo"),
        )
        create_default_blocks(context=obj)
        api.content.transition(obj=obj, transition="publish")
        item["path"] = f"/{obj.getId()}"
        obj.exclude_from_nav = True
        if obj.portal_type == "FaqFolder":
            setattr(obj, "icon", None)
            obj.reindexObject()
        if obj.portal_type == "Link":
            setattr(obj, "remoteUrl", "")

    # generate the payload for settings
    payload_items = [
        {
            "id": str(int(time.time() * 1000)) + "1",
            "newsletterSubscribe": False,
            "showSocial": False,
            "text": {"data": "<p><br/></p>"},
            "title": "Contatti",
            "titleLink": [],
            "visible": True,
        }
    ]
    markup = ""
    for item in TASSONOMIA_FOOTER[: len(TASSONOMIA_FOOTER) // 2]:
        if "data-element" in item:
            markup += '<li><a data-element="{}" href="{}">{}</a></li>'.format(
                item.get("data-element"), item.get("path"), item.get("title")
            )
        else:
            markup += '<li><a href="{}">{}</a></li>'.format(
                item.get("path"), item.get("title")
            )
    text = '<ul keys="696me,24qcs,6j5h0,f4p0j">{}</ul>'.format(markup)
    payload_items.append(
        {
            "id": str(int(time.time() * 1000)) + "2",
            "newsletterSubscribe": False,
            "showSocial": False,
            "text": {"data": text},
            "titleLink": [],
            "visible": True,
        }
    )

    markup = ""
    for item in TASSONOMIA_FOOTER[len(TASSONOMIA_FOOTER) // 2 :]:
        if "data-element" in item:
            markup += '<li><a data-element="{}" href="{}">{}</a></li>'.format(
                item.get("data-element"), item.get("path"), item.get("title")
            )
        else:
            markup += '<li><a href="{}">{}</a></li>'.format(
                item.get("path"), item.get("title")
            )
    text = '<ul keys="at8uf,f1h7r,d22s9,6lou">{}</ul>'.format(markup)
    payload_items.extend(
        [
            {
                "id": str(int(time.time() * 1000)) + "3",
                "newsletterSubscribe": False,
                "showSocial": False,
                "text": {"data": text},
                "titleLink": [],
                "visible": True,
            },
            {
                "id": str(int(time.time() * 1000)) + "4",
                "newsletterSubscribe": False,
                "showSocial": True,
                "text": {"data": "<p><br/></p>"},
                "title": "Seguici su",
                "titleLink": [],
                "visible": True,
            },
        ]
    )
    payload = [{"items": payload_items, "rootPath": "/"}]

    payload = json.dumps(payload)
    api.portal.set_registry_record(
        "footer_columns", payload, interface=IEditableFooterSettings
    )

    # generate content for subfooter
    # Generate needed pages
    obj = api.content.create(
        container=container,
        type="Document",
        title="Media Policy",
    )
    create_default_blocks(context=obj)
    obj.exclude_from_nav = True
    obj.reindexObject()

    payload = json.dumps(
        [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "Media Policy",
                        "visible": True,
                        "href": f"/{obj.getId()}",
                    },
                    {"title": "Sitemap", "visible": True, "href": "/sitemap"},
                    {
                        "title": "Credits",
                        "visible": True,
                        "href": "https://www.io-comune.it/",
                    },
                ],
            }
        ]
    )
    api.portal.set_registry_record(
        "subfooter_configuration", payload, interface=ISubfooter
    )


def create_default_menu_item(context, obj):
    title_uuid = str(uuid4())
    title = obj.Title()
    uid = obj.UID()
    context["blocks_layout"] = {"items": [title_uuid]}
    context["blocks"] = {title_uuid: {"@type": "text"}}
    context["title"] = title
    context["mode"] = "simpleLink"
    context["visible"] = True
    context["linkUrl"] = [uid]
    if title == "Amministrazione":
        context["id_lighthouse"] = "management"
        context["showMoreText"] = "Vedi tutto"
        context["navigationRoot"] = [uid]
        context["showMoreLink"] = [uid]
    elif title == "Servizi":
        context["id_lighthouse"] = "all-services"
        context["navigationRoot"] = [uid]
        context["showMoreLink"] = [uid]
    elif title == "Novità":
        context["id_lighthouse"] = "news"
        context["navigationRoot"] = [uid]
        context["showMoreLink"] = [uid]
    elif title == "Vivere il Comune":
        context["id_lighthouse"] = "live"
    elif title == "Argomenti":
        context["id_lighthouse"] = "all-topics"
        del context["mode"]
        context["title"] = "Tutti gli argomenti..."

    return context


def create_menu():
    request = getRequest()
    amministrazione = api.content.get(path="/amministrazione")
    servizi = api.content.get(path="/servizi")
    novita = api.content.get(path="/novita")
    vivere = api.content.get(path="/vivere-il-comune")

    items = []
    for x in [amministrazione, novita, servizi, vivere]:
        json_serialized = getMultiAdapter(
            (x, request or x.REQUEST), ISerializeToJsonSummary
        )()
        items.append(create_default_menu_item(context=json_serialized, obj=x))

    mocked_payload = [
        {
            "rootPath": "/",
            "items": items,
        }
    ]
    payload = json.dumps(mocked_payload)
    api.portal.set_registry_record(
        "menu_configuration", payload, interface=IDropDownMenu
    )


def create_secondary_menu():
    request = getRequest()
    items = []
    argomenti = api.content.get(path="/argomenti")
    json_serialized = getMultiAdapter(
        (argomenti, request or argomenti.REQUEST), ISerializeToJsonSummary
    )()
    items.append(create_default_menu_item(context=json_serialized, obj=argomenti))
    mocked_payload = [{"rootPath": "/", "items": items}]
    payload = json.dumps(mocked_payload)
    api.portal.set_registry_record(
        "secondary_menu_configuration", payload, interface=ISecondaryMenu
    )

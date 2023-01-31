# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from collective.volto.secondarymenu.interfaces import ISecondaryMenu
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from redturtle.voltoplugin.editablefooter.interfaces import IEditableFooterSettings
from uuid import uuid4
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest

import json


TASSONOMIA_PRIMO_LIVELLO = [
    "Amministrazione",
    "Servizi",
    "Novità",
    "Vivere il comune",
    "Argomenti",
]

TASSONOMIA_SERVIZI = [
    "Anagrafe e stato civile",
    "Cultura e tempo libero",
    "Vita lavorativa",
    "Catasto e urbanistica",
    "Turismo",
    "Mobilità e trasporti",
    "Educazione e formazione",
    "Giustizia e sicurezza pubblica",
    "Tributi, finanze e contravvenzioni",
    "Ambiente",
    "Salute, benessere e assistenza",
    "Autorizzazioni",
    "Agricoltura e pesca",
    "Imprese e commercio",
    "Appalti pubblici",
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

TASSONOMIA_NEWS = ["Notizie", "Comunicati (stampa)", "Avvisi"]
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
    elif title == "Vivere il comune":
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
    title_uuid = str(uuid4())
    context.blocks = {title_uuid: {"@type": "title"}}
    context.blocks_layout = {"items": [title_uuid]}


def create_footer():
    # Mocked up payload with generic structure
    mocked_payload = [
        {
            "items": [
                {
                    "id": 1643103855592,
                    "newsletterSubscribe": False,
                    "showSocial": False,
                    "text": {
                        "data": "<p>Comune di Nome Comune</p><p>Via Roma 123 - 00100 Comune</p><p>Codice fiscale / P.IVA:000123456789</p><p><br/></p><p>Ufficio Relazioni con il Pubblico</p><p>Numero verde: 800 016 123</p><p>SMS e WhatsApp: +39 320 1234567</p><p>Posta Elettronica Certificata</p><p>Centralino unico: 012 3456</p>"  # noqa
                    },
                    "title": "Contatti",
                    "titleLink": [],
                    "visible": True,
                },
                {
                    "id": 1673961753495,
                    "newsletterSubscribe": False,
                    "showSocial": False,
                    "text": {
                        "data": '<ul keys="696me,24qcs,6j5h0,f4p0j" depth="0"><li><a data-element="faq" href="/leggi-le-faq">Leggi le FAQ</a></li><li><a href="/faq" target="_blank" rel="noopener noreferrer" data-element="appointment-booking">Prenotazione appuntamento</a></li><li><a data-element="report-inefficiency" href="/segnalazione-disservizio">Segnalazione disservizio</a></li><li><a href="/richiedi-assistenza">Richiesta d&#x27;assistenza</a></li></ul>'  # noqa
                    },
                    "titleLink": [],
                    "visible": True,
                },
                {
                    "id": 1673962265420,
                    "newsletterSubscribe": False,
                    "showSocial": False,
                    "text": {
                        "data": '<ul keys="at8uf,f1h7r,d22s9,6lou" depth="0"><li><a href="/amministrazione-trasparente">Amministrazione trasparente</a></li><li><a data-element="privacy-policy-link" href="/privacy-policy">Informativa privacy</a></li><li>Note legali</li><li><a href="https://form.agid.gov.it/view/b3a483ab-9bc7-4cee-8faa-be91ca045ab5/" target="_blank" rel="noopener noreferrer" data-element="accessibility-link">Dichiarazione di accessibità</a></li></ul>'  # noqa
                    },
                    "titleLink": [],
                    "visible": True,
                },
                {
                    "id": 1643104715618,
                    "newsletterSubscribe": False,
                    "showSocial": True,
                    "text": {"data": "<p><br/></p>"},
                    "title": "Seguici su",
                    "titleLink": [],
                    "visible": True,
                },
            ],
            "rootPath": "/",
        }
    ]

    payload = json.dumps(mocked_payload)
    api.portal.set_registry_record(
        "footer_columns", payload, interface=IEditableFooterSettings
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
    elif title == "Vivere il comune":
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
        json_serialized = getMultiAdapter((x, request), ISerializeToJsonSummary)()
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
    json_serialized = getMultiAdapter((argomenti, request), ISerializeToJsonSummary)()
    items.append(create_default_menu_item(context=json_serialized, obj=argomenti))
    mocked_payload = [{"rootPath": "/", "items": items}]
    payload = json.dumps(mocked_payload)
    api.portal.set_registry_record(
        "secondary_menu_configuration", payload, interface=ISecondaryMenu
    )

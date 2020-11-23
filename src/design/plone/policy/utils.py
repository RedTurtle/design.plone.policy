# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import ISelectableConstrainTypes

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


def folderSubstructureGenerator(title, types=[]):
    container = api.portal.get()
    tree_root = api.content.create(
        container=container, type="Document", title=title
    )
    api.content.transition(obj=tree_root, transition="publish")
    if types:
        restrict_types(context=tree_root, types=types)

    if title == "Servizi":
        for ts in TASSONOMIA_SERVIZI:
            folder = api.content.create(
                container=tree_root, type="Document", title=ts
            )
            # temporary disabled
            # restrict_types(context=folder, types=("Servizio",))

    elif title == "Documenti e dati":
        for td in TASSONOMIA_DOCUMENTI:
            folder = api.content.create(
                container=tree_root, type="Document", title=td
            )

    elif title == "Novità":
        for tn in TASSONOMIA_NEWS:
            folder = api.content.create(
                container=tree_root, type="Document", title=tn
            )

            if tn == "Eventi":
                # temporary disabled
                # restrict_types(context=folder, types=("Event",))
                pass
            else:
                restrict_types(
                    context=folder,
                    types=("News Item", "Document", "Image", "File", "Link"),
                )

    elif title == "Amministrazione":
        api.content.create(
            type="Document", title="Politici", container=tree_root
        )
        # restrict_types(context=tree_root['politici'], types=("Persona",))

        api.content.create(
            type="Document",
            title="Personale Amministrativo",
            container=tree_root,
        )
        restrict_types(
            context=tree_root["personale-amministrativo"],
            types=("Document", "Persona",),
        )

        api.content.create(
            type="Document", title="Organi di governo", container=tree_root
        )
        restrict_types(
            context=tree_root["organi-di-governo"],
            types=("Document", "UnitaOrganizzativa",),
        )

        api.content.create(
            type="Document", title="Aree amministrative", container=tree_root
        )
        restrict_types(
            context=tree_root["aree-amministrative"],
            types=("Document", "UnitaOrganizzativa",),
        )

        api.content.create(
            type="Document", title="Uffici", container=tree_root
        )
        restrict_types(
            context=tree_root["uffici"],
            types=("Document", "UnitaOrganizzativa",),
        )

        api.content.create(
            type="Document", title="Enti e fondazioni", container=tree_root
        )
        restrict_types(
            context=tree_root["enti-e-fondazioni"],
            types=("Document", "UnitaOrganizzativa",),
        )

        api.content.create(
            type="Document", title="Luoghi", container=tree_root
        )
        restrict_types(
            context=tree_root["luoghi"], types=("Document", "Venue",)
        )

    elif title == "Argomenti":
        restrict_types(
            context=tree_root, types=("Document", "Pagina Argomento",)
        )


def restrict_types(context, types):
    constraints = ISelectableConstrainTypes(context)
    constraints.setConstrainTypesMode(1)
    constraints.setLocallyAllowedTypes(types)

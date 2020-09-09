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


def folderSubstructureGenerator(title):
    container = api.portal.get()
    tree_root = api.content.create(
        container=container, type="Document", title=title
    )
    api.content.transition(obj=tree_root, transition="publish")
    restrict_types(context=tree_root, types=("Document",))

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
            if td == "Dataset":
                # restrict_types(context=folder, types=("Dataset",))
                pass
            else:
                # restrict_types(context=folder, types=("Documento",))
                pass

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
                restrict_types(context=folder, types=("News Item",))

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
            context=tree_root["personale-amministrativo"], types=("Persona",)
        )

        api.content.create(
            type="Document", title="Organi di governo", container=tree_root
        )
        restrict_types(
            context=tree_root["organi-di-governo"],
            types=("UnitaOrganizzativa",),
        )

        api.content.create(
            type="Document", title="Aree amministrative", container=tree_root
        )
        restrict_types(
            context=tree_root["aree-amministrative"],
            types=("UnitaOrganizzativa",),
        )

        api.content.create(
            type="Document", title="Uffici", container=tree_root
        )
        restrict_types(
            context=tree_root["uffici"], types=("UnitaOrganizzativa",)
        )

        api.content.create(
            type="Document", title="Enti e fondazioni", container=tree_root
        )
        restrict_types(
            context=tree_root["enti-e-fondazioni"],
            types=("UnitaOrganizzativa",),
        )

        api.content.create(
            type="Document", title="Luoghi", container=tree_root
        )
        restrict_types(context=tree_root["luoghi"], types=("Venue",))

    elif title == "Argomenti":
        restrict_types(context=tree_root, types=("Pagina Argomento",))


def restrict_types(context, types):
    constraints = ISelectableConstrainTypes(context)
    constraints.setConstrainTypesMode(1)
    constraints.setLocallyAllowedTypes(types)
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
    if title == "Servizi":
        tree_rootConstraints = ISelectableConstrainTypes(tree_root)
        tree_rootConstraints.setConstrainTypesMode(1)
        tree_rootConstraints.setLocallyAllowedTypes(("Document",))
        for ts in TASSONOMIA_SERVIZI:
            folder = api.content.create(
                container=tree_root, type="Document", title=ts
            )

            folderConstraints = ISelectableConstrainTypes(folder)
            folderConstraints.setConstrainTypesMode(1)
            folderConstraints.setLocallyAllowedTypes(("Servizio",))

    elif title == "Documenti e dati":
        tree_rootConstraints = ISelectableConstrainTypes(tree_root)
        tree_rootConstraints.setConstrainTypesMode(1)
        tree_rootConstraints.setLocallyAllowedTypes(("Document",))

        for td in TASSONOMIA_DOCUMENTI:
            folder = api.content.create(
                container=tree_root, type="Document", title=td
            )

            folderConstraints = ISelectableConstrainTypes(folder)
            folderConstraints.setConstrainTypesMode(1)
            if td == "Dataset":
                folderConstraints.setLocallyAllowedTypes(("Dataset",))
            else:
                folderConstraints.setLocallyAllowedTypes(("Documento",))

    elif title == "Novità":
        tree_rootConstraints = ISelectableConstrainTypes(tree_root)
        tree_rootConstraints.setConstrainTypesMode(1)
        tree_rootConstraints.setLocallyAllowedTypes(("Document",))
        for tn in TASSONOMIA_NEWS:
            folder = api.content.create(
                container=tree_root, type="Document", title=tn
            )

            folderConstraints = ISelectableConstrainTypes(folder)
            folderConstraints.setConstrainTypesMode(1)
            if tn == "Eventi":
                folderConstraints.setLocallyAllowedTypes(("Event",))
            else:
                folderConstraints.setLocallyAllowedTypes(("News Item",))

    elif title == "Amministrazione":
        tree_rootConstraints = ISelectableConstrainTypes(tree_root)
        tree_rootConstraints.setConstrainTypesMode(1)
        tree_rootConstraints.setLocallyAllowedTypes(
            ("PersoneFolder", "UnitaOrganizzativaFolder", "LuoghiFolder")
        )

        api.content.create(
            type="PersoneFolder", title="Politici", container=tree_root
        )
        api.content.create(
            type="PersoneFolder",
            title="Personale Amministrativo",
            container=tree_root,
        )
        api.content.create(
            type="UnitaOrganizzativaFolder",
            title="Organi di governo",
            container=tree_root,
        )
        api.content.create(
            type="UnitaOrganizzativaFolder",
            title="Aree amministrative",
            container=tree_root,
        )
        api.content.create(
            type="UnitaOrganizzativaFolder",
            title="Uffici",
            container=tree_root,
        )
        api.content.create(
            type="UnitaOrganizzativaFolder",
            title="Enti e fondazioni",
            container=tree_root,
        )
        api.content.create(
            type="LuoghiFolder", title="Luoghi", container=tree_root
        )

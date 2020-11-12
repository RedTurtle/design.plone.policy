# -*- coding: utf-8 -*-
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestInitialStructureCreation(unittest.TestCase):

    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_first_level_created(self):
        self.assertEqual(
            [x.id for x in self.portal.getFolderContents()],
            [
                "amministrazione",
                "servizi",
                "novita",
                "documenti-e-dati",
                "argomenti",
            ],
        )

    def test_amministrazione_section(self):

        amministrazione = self.portal["amministrazione"]
        self.assertEqual(amministrazione.constrain_types_mode, 1)
        self.assertEqual(
            amministrazione.locally_allowed_types,
            ("Document", "Image", "File", "Link"),
        )

        self.assertEqual(
            amministrazione.keys(),
            [
                "politici",
                "personale-amministrativo",
                "organi-di-governo",
                "aree-amministrative",
                "uffici",
                "enti-e-fondazioni",
                "luoghi",
            ],
        )

        self.assertEqual(amministrazione["politici"].portal_type, "Document")
        self.assertEqual(amministrazione["politici"].constrain_types_mode, 1)
        self.assertEqual(
            amministrazione["politici"].locally_allowed_types,
            ("Document", "Image", "File", "Link"),
        )

        self.assertEqual(
            amministrazione["personale-amministrativo"].portal_type, "Document"
        )
        self.assertEqual(
            amministrazione["personale-amministrativo"].constrain_types_mode, 1
        )
        self.assertEqual(
            amministrazione["personale-amministrativo"].locally_allowed_types,
            ("Persona",),
        )

        self.assertEqual(
            amministrazione["organi-di-governo"].portal_type, "Document"
        )
        self.assertEqual(
            amministrazione["organi-di-governo"].constrain_types_mode, 1
        )
        self.assertEqual(
            amministrazione["organi-di-governo"].locally_allowed_types,
            ("UnitaOrganizzativa",),
        )

        self.assertEqual(
            amministrazione["aree-amministrative"].portal_type, "Document"
        )
        self.assertEqual(
            amministrazione["aree-amministrative"].constrain_types_mode, 1
        )
        self.assertEqual(
            amministrazione["aree-amministrative"].locally_allowed_types,
            ("UnitaOrganizzativa",),
        )

        self.assertEqual(amministrazione["uffici"].portal_type, "Document")
        self.assertEqual(amministrazione["uffici"].constrain_types_mode, 1)
        self.assertEqual(
            amministrazione["uffici"].locally_allowed_types,
            ("UnitaOrganizzativa",),
        )

        self.assertEqual(
            amministrazione["enti-e-fondazioni"].portal_type, "Document"
        )
        self.assertEqual(
            amministrazione["enti-e-fondazioni"].constrain_types_mode, 1
        )
        self.assertEqual(
            amministrazione["enti-e-fondazioni"].locally_allowed_types,
            ("UnitaOrganizzativa",),
        )

        self.assertEqual(amministrazione["luoghi"].portal_type, "Document")
        self.assertEqual(amministrazione["luoghi"].constrain_types_mode, 1)
        self.assertEqual(
            amministrazione["luoghi"].locally_allowed_types, ("Venue",)
        )

    def test_servizi_section(self):

        servizi = self.portal["servizi"]
        self.assertEqual(servizi.constrain_types_mode, 1)
        self.assertEqual(
            servizi.locally_allowed_types,
            ("Document", "Image", "File", "Link"),
        )
        self.assertEqual(
            servizi.keys(),
            [
                "anagrafe-e-stato-civile",
                "cultura-e-tempo-libero",
                "vita-lavorativa",
                "attivita-produttive-e-commercio",
                "appalti-pubblici",
                "catasto-e-urbanistica",
                "turismo",
                "mobilita-e-trasporti",
                "educazione-e-formazione",
                "giustizia-e-sicurezza-pubblica",
                "tributi-e-finanze",
                "ambiente",
                "salute-benessere-e-assistenza",
                "autorizzazioni",
                "agricoltura",
            ],
        )

        for child in servizi.listFolderContents():
            self.assertEqual(child.portal_type, "Document")
            self.assertEqual(child.constrain_types_mode, 1)
            self.assertEqual(
                child.locally_allowed_types,
                ("Document", "Image", "File", "Link"),
            )

    def test_novita_section(self):

        folder = self.portal["novita"]
        self.assertEqual(folder.constrain_types_mode, 1)
        self.assertEqual(
            folder.locally_allowed_types, ("Document", "Image", "File", "Link")
        )
        self.assertEqual(folder.keys(), ["notizie", "comunicati", "eventi"])

        for child in folder.listFolderContents():
            self.assertEqual(child.portal_type, "Document")
            self.assertEqual(child.constrain_types_mode, 1)
            if child.getId() == "eventi":
                self.assertEqual(
                    child.locally_allowed_types,
                    ("Document", "Image", "File", "Link"),
                )
            else:
                self.assertEqual(child.locally_allowed_types, ("News Item",))

    def test_documenti_e_dati_section(self):

        folder = self.portal["documenti-e-dati"]
        self.assertEqual(folder.constrain_types_mode, 1)
        self.assertEqual(
            folder.locally_allowed_types,
            (
                "Document",
                "Image",
                "File",
                "Link",
                "Documento",
                "CartellaModulistica",
            ),
        )
        self.assertEqual(
            folder.keys(),
            [
                "documenti-albo-pretorio",
                "modulistica",
                "documenti-funzionamento-interno",
                "atti-normativi",
                "accordi-tra-enti",
                "documenti-attivita-politica",
                "documenti-tecnici-di-supporto",
                "istanze",
                "dataset",
            ],
        )

        for child in folder.listFolderContents():
            self.assertEqual(child.portal_type, "Document")
            self.assertEqual(child.constrain_types_mode, 1)
            self.assertEqual(
                child.locally_allowed_types,
                (
                    "Document",
                    "Image",
                    "File",
                    "Link",
                    "Documento",
                    "CartellaModulistica",
                ),
            )

    def test_argomenti_section(self):
        folder = self.portal["argomenti"]
        self.assertEqual(folder.portal_type, "Document")
        self.assertEqual(folder.constrain_types_mode, 1)
        self.assertEqual(folder.locally_allowed_types, ("Pagina Argomento",))

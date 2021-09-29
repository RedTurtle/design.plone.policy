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
        self.assertEqual(
            amministrazione["personale-amministrativo"].portal_type, "Document"
        )
        self.assertEqual(amministrazione["organi-di-governo"].portal_type, "Document")
        self.assertEqual(amministrazione["aree-amministrative"].portal_type, "Document")
        self.assertEqual(amministrazione["uffici"].portal_type, "Document")
        self.assertEqual(amministrazione["enti-e-fondazioni"].portal_type, "Document")
        self.assertEqual(amministrazione["luoghi"].portal_type, "Document")

    def test_servizi_section(self):

        servizi = self.portal["servizi"]
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

    def test_novita_section(self):

        folder = self.portal["novita"]
        self.assertEqual(folder.keys(), ["notizie", "comunicati", "eventi"])

        for child in folder.listFolderContents():
            self.assertEqual(child.portal_type, "Document")

    def test_documenti_e_dati_section(self):

        folder = self.portal["documenti-e-dati"]
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

    def test_argomenti_section(self):
        folder = self.portal["argomenti"]
        self.assertEqual(folder.portal_type, "Document")

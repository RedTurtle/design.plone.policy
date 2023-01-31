# -*- coding: utf-8 -*-
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from design.plone.policy.utils import TASSONOMIA_AMMINISTRAZIONE
from design.plone.policy.utils import TASSONOMIA_ARGOMENTI
from design.plone.policy.utils import TASSONOMIA_DOCUMENTI
from design.plone.policy.utils import TASSONOMIA_NEWS
from design.plone.policy.utils import TASSONOMIA_ORGANI_GOVERNO
from design.plone.policy.utils import TASSONOMIA_PRIMO_LIVELLO
from design.plone.policy.utils import TASSONOMIA_SERVIZI
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


# TODO: rework tests
class TestInitialStructureCreation(unittest.TestCase):

    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def normalize_ids(self, string):
        return string.replace(" ", "-").lower()

    def check_initial_blocks(self, obj):
        self.assertEqual(obj.portal_type, "Document")
        self.assertEqual(len(obj.blocks.values()), 1)
        self.assertEqual(len(obj.blocks_layout["items"]), 1)

    def check_children_initial_blocks(self, obj):
        for child in obj.listFolderContents():
            self.check_initial_blocks(child)

    def test_first_level_created(self):
        self.assertEqual(
            [x.id for x in self.portal.getFolderContents()],
            [self.normalize_ids(x) for x in TASSONOMIA_PRIMO_LIVELLO],
        )
        self.check_children_initial_blocks(self.portal)

    def test_amministrazione_section(self):
        amministrazione = self.portal["amministrazione"]
        self.assertEqual(
            amministrazione.keys(),
            [self.normalize_ids(x) for x in TASSONOMIA_AMMINISTRAZIONE],
        )
        for x in TASSONOMIA_AMMINISTRAZIONE:
            self.assertEqual(
                amministrazione.get(self.normalize_ids(x), None).portal_type, "Document"
            )
        self.check_children_initial_blocks(amministrazione)

        self.assertEqual(
            amministrazione["organi-di-governo"].keys(),
            [self.normalize_ids(x) for x in TASSONOMIA_ORGANI_GOVERNO],
        )
        for child in amministrazione["organi-di-governo"].listFolderContents():
            self.assertEqual(child.portal_type, "Document")
            self.check_initial_blocks(child)

    def test_servizi_section(self):

        servizi = self.portal["servizi"]
        self.assertEqual(
            servizi.keys(),
            [self.normalize_ids(x) for x in TASSONOMIA_SERVIZI],
        )

        for child in servizi.listFolderContents():
            self.assertEqual(child.portal_type, "Document")
            self.check_initial_blocks(child)

    def test_novita_section(self):

        folder = self.portal["novita"]
        self.assertEqual(
            folder.keys(), [self.normalize_ids(x) for x in TASSONOMIA_NEWS]
        )

        for child in folder.listFolderContents():
            self.assertEqual(child.portal_type, "Document")
            self.check_initial_blocks(child)

    def test_documenti_e_dati_section(self):

        folder = self.portal["documenti-e-dati"]
        self.assertEqual(
            folder.keys(),
            [self.normalize_ids(x) for x in TASSONOMIA_DOCUMENTI],
        )

        self.check_children_initial_blocks(folder)

    def test_argomenti_section(self):
        folder = self.portal["argomenti"]
        self.assertEqual(folder.portal_type, "Document")
        self.assertEqual(
            folder.keys(),
            [self.normalize_ids(x) for x in TASSONOMIA_ARGOMENTI],
        )
        self.check_children_initial_blocks(folder)

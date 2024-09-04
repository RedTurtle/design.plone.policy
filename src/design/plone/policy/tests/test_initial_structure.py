# -*- coding: utf-8 -*-
from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from design.plone.policy.utils import TASSONOMIA_AMMINISTRAZIONE
from design.plone.policy.utils import TASSONOMIA_ARGOMENTI
from design.plone.policy.utils import TASSONOMIA_NEWS
from design.plone.policy.utils import TASSONOMIA_ORGANI_GOVERNO
from design.plone.policy.utils import TASSONOMIA_SERVIZI
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.restapi.behaviors import IBlocks
from zope.component import getUtility

import unittest


# TODO: rework tests
class TestInitialStructureCreation(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def normalize_ids(self, string):
        return getUtility(IURLNormalizer).normalize(string)

    def check_initial_blocks(self, obj):
        self.assertTrue(IBlocks.providedBy(obj))
        self.assertEqual(len(obj.blocks.values()), 1)
        self.assertEqual(len(obj.blocks_layout["items"]), 1)

    def check_children_initial_blocks(self, obj):
        for child in obj.listFolderContents():
            self.check_initial_blocks(child)

    def test_first_level_created(self):
        no_blocks = [
            "prenotazione-appuntamento",
            "segnalazione-disservizio",
            "richiesta-di-assistenza",
            "amministrazione-trasparente",
            "informativa-privacy",
            "note-legali",
            "media-policy",
        ]
        for child in self.portal.listFolderContents():
            if child.id == "leggi-le-faq":
                self.assertEqual(child.portal_type, "FaqFolder")
            elif child.id == "dichiarazione-di-accessibilita":
                self.assertEqual(child.portal_type, "Link")
            else:
                self.assertEqual(child.portal_type, "Document")
                if child.id not in no_blocks:
                    self.assertEqual(len(child.blocks.values()), 1)
                    self.assertEqual(len(child.blocks_layout["items"]), 1)

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

    def test_argomenti_section(self):
        folder = self.portal["argomenti"]
        self.assertEqual(folder.portal_type, "Document")
        self.assertEqual(
            folder.keys(), [self.normalize_ids(x) for x in TASSONOMIA_ARGOMENTI]
        )
        self.assertEqual(folder.portal_type, "Document")
        for child in folder.listFolderContents():
            self.assertEqual(child.portal_type, "Pagina Argomento")
            self.assertEqual(len(child.blocks.values()), 1)
            self.assertEqual(len(child.blocks_layout["items"]), 1)

    def test_enabled_blocks_contents_have_defaults(self):
        brains = self.portal.portal_catalog(
            object_provides="plone.restapi.behaviors.IBlocks"
        )
        for brain in brains:
            self.check_initial_blocks(brain.getObject())

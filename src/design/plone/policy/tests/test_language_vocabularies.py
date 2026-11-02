from design.plone.policy.testing import DESIGN_PLONE_POLICY_INTEGRATION_TESTING
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestLanguageVocabularies(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def _labels(self, name):
        factory = getUtility(IVocabularyFactory, name=name)
        return {term.value: term.title for term in factory(self.portal)}

    def test_available_content_languages_have_code(self):
        labels = self._labels("plone.app.vocabularies.AvailableContentLanguages")
        self.assertEqual(labels["en"], "English (en)")
        self.assertEqual(labels["it"], "Italiano (it)")

    def test_supported_content_languages_have_code(self):
        labels = self._labels("plone.app.vocabularies.SupportedContentLanguages")
        self.assertTrue(labels)
        for code, label in labels.items():
            self.assertTrue(label.endswith(f"({code})"), label)

# -*- coding: utf-8 -*-
from design.plone.policy.testing import (
    DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import RelativeSession
from Products.CMFPlone.interfaces import ISearchSchema
from transaction import commit
from zope.component import getUtility

import unittest


class SearchFiltersAPITest(unittest.TestCase):

    layer = DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.api_session_anon = RelativeSession(self.portal_url)
        self.api_session_anon.headers.update({"Accept": "application/json"})

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def tearDown(self):
        self.api_session.close()
        self.api_session_anon.close()

    def test_endpoint_exists(self):
        response = self.api_session.get("/@search-filters")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

    def test_endpoint_return_list_of_sections(self):
        response = self.api_session.get("/@search-filters").json()

        self.assertIn("sections", response)
        sections = response["sections"]

        self.assertEqual(len(sections), 1)
        self.assertEqual(len(sections[0]["items"]), 4)
        self.assertEqual("Amministrazione", sections[0]["items"][0]["title"])
        self.assertEqual("Servizi", sections[0]["items"][1]["title"])
        self.assertEqual("Novità", sections[0]["items"][2]["title"])
        self.assertEqual("Documenti e dati", sections[0]["items"][3]["title"])

    def test_endpoint_return_list_of_topics_empty_if_no_topics(self):
        response = self.api_session.get("/@search-filters").json()

        self.assertIn("topics", response)
        self.assertEqual(response["topics"], [])

    def test_endpoint_return_list_of_topics_based_on_roles(self):

        api.content.create(
            container=self.portal, type="Pagina Argomento", title="private topic"
        )
        public_topic = api.content.create(
            container=self.portal, type="Pagina Argomento", title="public topic"
        )
        api.content.transition(obj=public_topic, transition="publish")
        commit()

        response = self.api_session.get("/@search-filters").json()
        self.assertIn("topics", response)
        self.assertEqual(len(response["topics"]), 2)

        response = self.api_session_anon.get("/@search-filters").json()

        self.assertIn("topics", response)
        self.assertEqual(len(response["topics"]), 1)

    def test_endpoint_return_list_of_searchable_types(self):
        response = self.api_session.get("/@search-filters").json()

        self.assertIn("portal_types", response)
        types = [x["id"] for x in response["portal_types"]]
        self.assertIn("Document", types)

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSchema, prefix="plone")
        settings.types_not_searched = tuple(
            list(settings.types_not_searched) + ["Document"]
        )
        commit()

        response = self.api_session.get("/@search-filters").json()

        self.assertIn("portal_types", response)
        types = [x["id"] for x in response["portal_types"]]
        self.assertNotIn("Document", types)

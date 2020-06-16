# -*- coding: utf-8 -*-
from design.plone.policy.testing import (
    DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

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

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def tearDown(self):
        self.api_session.close()

    def test_endpoint_exists(self):
        response = self.api_session.get("/@search-filters")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

    def test_endpoint_return_list_of_sections(self):
        response = self.api_session.get("/@search-filters").json()

        self.assertIn('sections', response)
        sections = response['sections']
        self.assertIn('amministrazione', sections)
        self.assertIn('documenti-e-dati', sections)
        self.assertIn('novita', sections)
        self.assertIn('servizi', sections)

    def test_endpoint_return_list_of_topics_empty_if_no_topics(self):
        response = self.api_session.get("/@search-filters").json()

        self.assertIn('topics', response)
        self.assertEqual(response['topics'], [])

    # temporary disabled
    # def test_endpoint_return_list_of_topics_empty_if_topics(self):

    #     api.content.create(
    #         container=self.portal, type="Pagina Argomento", title="foo"
    #     )
    #     api.content.create(
    #         container=self.portal, type="Pagina Argomento", title="bar"
    #     )

    #     commit()
    #     response = self.api_session.get("/@search-filters").json()

    #     self.assertIn('topics', response)
    #     self.assertEqual(len(response['topics']), 2)

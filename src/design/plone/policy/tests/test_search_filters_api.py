# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone import api
from plone.restapi.testing import RelativeSession
from design.plone.policy.testing import (
    DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING,
)
from transaction import commit

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

    def test_endpoint_return_list_of_arguments_empty_if_no_arguments(self):
        response = self.api_session.get("/@search-filters").json()

        self.assertIn('arguments', response)
        self.assertEqual(response['arguments'], [])

    def test_endpoint_return_list_of_arguments_empty_if_arguments(self):

        api.content.create(
            container=self.portal, type="Pagina Argomento", title="foo"
        )
        api.content.create(
            container=self.portal, type="Pagina Argomento", title="bar"
        )

        commit()
        response = self.api_session.get("/@search-filters").json()

        self.assertIn('arguments', response)
        self.assertEqual(len(response['arguments']), 2)

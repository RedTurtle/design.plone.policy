# -*- coding: utf-8 -*-
from design.plone.policy.testing import (
    DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from zope.component import getUtility
from transaction import commit
from z3c.relationfield import RelationValue
from zope.intid.interfaces import IIntIds
from plone import api

import unittest


class BandiSearchFiltersAPITest(unittest.TestCase):

    layer = DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        intids = getUtility(IIntIds)
        self.uo_public_1 = api.content.create(
            container=self.portal, type="UnitaOrganizzativa", title="UO 1"
        )
        self.uo_public_2 = api.content.create(
            container=self.portal, type="UnitaOrganizzativa", title="UO 2"
        )
        self.uo_private = api.content.create(
            container=self.portal, type="UnitaOrganizzativa", title="UO 3"
        )
        self.bando_public_1 = api.content.create(
            container=self.portal,
            type="Bando",
            title="Bando 1",
            subject=("foo"),
            ufficio_responsabile=[RelationValue(intids.getId(self.uo_public_1))],
        )
        self.bando_public_2 = api.content.create(
            container=self.portal,
            type="Bando",
            title="Bando 2",
            subject=("foo", "bar"),
            ufficio_responsabile=[
                RelationValue(intids.getId(self.uo_public_2)),
                RelationValue(intids.getId(self.uo_private)),
            ],
        )
        self.bando_private = api.content.create(
            container=self.portal,
            type="Bando",
            title="Bando 3",
            subject=("foo", "baz"),
            ufficio_responsabile=[RelationValue(intids.getId(self.uo_public_1))],
        )

        api.content.transition(obj=self.uo_public_1, transition="publish")
        api.content.transition(obj=self.uo_public_2, transition="publish")
        api.content.transition(obj=self.bando_public_1, transition="publish")
        api.content.transition(obj=self.bando_public_2, transition="publish")

        commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_endpoint_exists(self):
        response = self.api_session.get("/@bandi-search-filters")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

    def test_endpoint_return_list_of_offices_based_on_permissions(self):
        response = self.api_session.get("/@bandi-search-filters").json()

        self.assertIn("offices", response)
        offices = response["offices"]

        self.assertEqual(len(offices), 3)

        response = self.anon_api_session.get("/@bandi-search-filters").json()

        self.assertIn("offices", response)
        offices = response["offices"]
        self.assertEqual(len(offices), 2)

    def test_endpoint_return_list_of_subjects_based_on_permissions(self):
        response = self.api_session.get("/@bandi-search-filters").json()

        self.assertIn("subjects", response)
        subjects = [x["UID"] for x in response["subjects"]]
        self.assertEqual(len(subjects), 3)
        self.assertEqual(subjects, ["bar", "baz", "foo"])

        response = self.anon_api_session.get("/@bandi-search-filters").json()

        self.assertIn("subjects", response)
        subjects = [x["UID"] for x in response["subjects"]]
        self.assertEqual(len(subjects), 2)
        self.assertEqual(subjects, ["bar", "foo"])

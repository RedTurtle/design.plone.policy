# -*- coding: utf-8 -*-
from design.plone.policy.testing import DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING
from design.plone.policy.enabled_vocabularies import allowed_vocabularies
from plone import api
from plone.app.testing import (
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession

import unittest
import transaction


class TestVocabularyEndpointCustom(unittest.TestCase):

    layer = DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # create some test users
        api.user.create(
            username="member",
            email="member@example.org",
            password="secret",
            roles=("Member",),
        )
        api.user.create(
            username="contributor",
            email="contributor@example.org",
            password="secret",
            roles=("Member", "Contributor"),
        )

        api.user.create(
            username="editor",
            email="editor@example.org",
            password="secret",
            roles=("Member", "Editor", "Reviewer"),
        )

        transaction.commit()

    def test_anonymous_can_get_standard_allowed_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        response = api_session.get("/@vocabularies/plone.app.vocabularies.Keywords")

        self.assertEqual(response.status_code, 200)

        api_session.close()

    def test_anonymous_can_get_custom_allowed_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        for name in allowed_vocabularies():
            response = api_session.get("/@vocabularies/{}".format(name))

            self.assertEqual(response.status_code, 200)

        api_session.close()

    def test_anonymous_cant_get_disallowed_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        response = api_session.get("/@vocabularies/design.plone.vocabularies.argomenti")
        self.assertEqual(response.status_code, 401)

        api_session.close()

    def test_authenticated_can_get_custom_allowed_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})

        for username in ["member", "contributor", "editor"]:
            api_session.auth = (username, "secret")

            for name in allowed_vocabularies():
                response = api_session.get("/@vocabularies/{}".format(name))
                self.assertEqual(response.status_code, 200)

        api_session.close()

    def test_basic_users_cant_get_other_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})

        api_session.auth = ("member", "secret")
        response = api_session.get("/@vocabularies/design.plone.vocabularies.argomenti")

        self.assertEqual(response.status_code, 401)

        api_session.close()

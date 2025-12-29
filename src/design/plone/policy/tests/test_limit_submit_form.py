from design.plone.policy.testing import DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility

import csv
import io
import transaction
import unittest


class TestLimitMailStore(unittest.TestCase):
    layer = DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.mailhost = getUtility(IMailHost)

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        # self.anon_api_session = RelativeSession(self.portal_url)
        # self.anon_api_session.headers.update({"Accept": "application/json"})

        self.document = api.content.create(
            type="Document",
            title="Example context",
            container=self.portal,
        )

        self.document.blocks = {
            "text-id": {"@type": "text"},
            "form-id": {"@type": "form"},
        }
        self.document_url = (
            f"{self.portal.absolute_url()}/++api++/{self.document.getId()}"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        # self.anon_api_session.close()

        # set default block
        # self.document.blocks = {
        #     "text-id": {"@type": "text"},
        #     "form-id": {"@type": "form"},
        # }
        # transaction.commit()

    def submit_form(self, data):
        url = f"{self.document_url}/@submit-form"
        response = self.api_session.post(
            url,
            json=data,
        )
        return response

    def test_limit_submit(self):
        self.document.blocks = {
            "form-id": {
                "@type": "form",
                "store": True,
                "limit": 1,
                "subblocks": [
                    {
                        "label": "Message",
                        "field_id": "message",
                        "field_type": "text",
                    },
                    {
                        "label": "Name",
                        "field_id": "name",
                        "field_type": "text",
                    },
                ],
            },
        }
        transaction.commit()

        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "data": [
                    {"field_id": "message", "value": "just want to say hi"},
                    {"field_id": "name", "value": "John"},
                    {"field_id": "foo", "value": "skip this"},
                ],
                "subject": "test subject",
                "block_id": "form-id",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "data": [
                    {"field_id": "message", "value": "just want to say hi"},
                    {"field_id": "name", "value": "John"},
                    {"field_id": "foo", "value": "skip this"},
                ],
                "subject": "test subject",
                "block_id": "form-id",
            },
        )
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.json()["waiting_list"])

        # export csv
        response = self.api_session.get(f"{self.document_url}/@form-data-export")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Type"],
            "text/comma-separated-values; charset=utf-8",
        )
        self.assertEqual(
            [r for r in csv.DictReader(io.StringIO(response.text))],
            [
                {
                    "Message": "just want to say hi",
                    "Name": "John",
                    "Lista d'attesa": "No",
                    "date": "2025-12-29T23:09:33",
                },
                {
                    "Message": "just want to say hi",
                    "Name": "John",
                    "Lista d'attesa": "Si",
                    "date": "2025-12-29T23:09:33",
                },
            ],
        )

    def test_unique_field(self):
        self.document.blocks = {
            "form-id": {
                "@type": "form",
                "store": True,
                "subblocks": [
                    {
                        "label": "Message",
                        "field_id": "message",
                        "field_type": "text",
                    },
                    {
                        "label": "Name",
                        "field_id": "name",
                        "field_type": "text",
                        "unique": True,
                    },
                ],
            },
        }
        transaction.commit()

        data = {
            "from": "john@doe.com",
            "data": [
                {"field_id": "message", "value": "just want to say hi"},
                {"field_id": "name", "value": "John"},
                {"field_id": "foo", "value": "skip this"},
            ],
            "subject": "test subject",
            "block_id": "form-id",
        }

        response = self.submit_form(data=data)
        self.assertEqual(response.status_code, 200)

        response = self.submit_form(data=data)
        self.assertEqual(response.status_code, 400)

        # test message is not fair because it's a translation, in another package
        message = response.json()["message"]
        self.assertEqual(
            message,
            'Unable to save data. The value of field "Name" is already stored in previous submissions.',
        )

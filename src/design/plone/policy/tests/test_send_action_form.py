# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from design.plone.policy.testing import (
    DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING,
)
from plone.restapi.testing import RelativeSession
from plone import api
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility

import transaction
import unittest


class SendActionFormEndpoint(unittest.TestCase):

    layer = DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.mailhost = getUtility(IMailHost)

        registry = getUtility(IRegistry)
        registry["plone.email_from_address"] = "info@test.org"
        registry["plone.email_from_name"] = u"Plone test site"

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        self.document = api.content.create(
            type="Document", title="Example context", container=self.portal,
        )
        self.document.blocks = {
            "text-id": {"@type": "text"},
            "form-id": {"@type": "form"},
        }
        self.document_url = self.document.absolute_url()
        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

        # set default block
        self.document.blocks = {
            "text-id": {"@type": "text"},
            "form-id": {"@type": "form"},
        }
        transaction.commit()

    def submit_form(self, data):
        url = "{}/@send-action-form".format(self.document_url)
        response = self.api_session.post(url, json=data,)
        transaction.commit()
        return response

    def test_email_not_send_if_block_id_is_not_given(self):
        response = self.submit_form(
            data={"from": "john@doe.com", "message": "Just want to say hi."},
        )
        transaction.commit()

        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(res["message"], "block_id mancante")

    def test_email_not_send_if_block_id_is_incorrect_or_not_present(self):
        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "block_id": "unknown",
            },
        )
        transaction.commit()

        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res["message"],
            'Blocco di tipo "form" con id "unknown" non trovato',
        )

        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "block_id": "text-id",
            },
        )
        transaction.commit()

        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res["message"],
            'Blocco di tipo "form" con id "text-id" non trovato',
        )

    def test_email_not_send_if_block_id_is_correct_but_required_fields_missing(
        self,
    ):
        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "block_id": "form-id",
            },
        )
        transaction.commit()

        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res["message"],
            "Campo obbligatorio tra message, subject e from mancante",
        )

    def test_email_sent_with_site_recipient(self,):
        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "subject": "test subject",
                "block_id": "form-id",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertIn("Subject: test subject", msg)
        self.assertIn("From: john@doe.com", msg)
        self.assertIn("To: info@test.org", msg)
        self.assertIn("Reply-To: john@doe.com", msg)
        self.assertIn("Just want to say hi.", msg)

    def test_email_sent_ignore_passed_recipient(self,):

        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "to": "to@spam.com",
                "message": "Just want to say hi.",
                "subject": "test subject",
                "block_id": "form-id",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertIn("Subject: test subject", msg)
        self.assertIn("From: john@doe.com", msg)
        self.assertIn("To: info@test.org", msg)
        self.assertIn("Reply-To: john@doe.com", msg)
        self.assertIn("Just want to say hi.", msg)

    def test_email_sent_with_block_recipient_if_set(self,):

        self.document.blocks = {
            "text-id": {"@type": "text"},
            "form-id": {"@type": "form", "to": "to@block.com"},
        }
        transaction.commit()

        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "subject": "test subject",
                "block_id": "form-id",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertIn("Subject: test subject", msg)
        self.assertIn("From: john@doe.com", msg)
        self.assertIn("To: to@block.com", msg)
        self.assertIn("Reply-To: john@doe.com", msg)
        self.assertIn("Just want to say hi.", msg)

    def test_email_sent_with_block_subject_if_set_and_not_passed(self,):

        self.document.blocks = {
            "text-id": {"@type": "text"},
            "form-id": {"@type": "form", "default_subject": "block subject"},
        }
        transaction.commit()

        response = self.submit_form(
            data={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "block_id": "form-id",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertIn("Subject: block subject", msg)
        self.assertIn("From: john@doe.com", msg)
        self.assertIn("To: info@test.org", msg)
        self.assertIn("Reply-To: john@doe.com", msg)
        self.assertIn("Just want to say hi.", msg)

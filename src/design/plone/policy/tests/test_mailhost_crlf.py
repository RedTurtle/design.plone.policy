# -*- coding: utf-8 -*-
from design.plone.policy.mailhost import normalize_eol
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.MailHost.MailHost import MailHost
from unittest import mock

import re
import smtplib
import unittest


BARE_LF = re.compile(rb"(?<!\r)\n")


class TestNormalizeEol(unittest.TestCase):
    def test_bare_lf_and_cr_become_crlf(self):
        self.assertEqual(normalize_eol(b"a\nb\rc\r\nd"), b"a\r\nb\r\nc\r\nd")
        self.assertEqual(normalize_eol("a\nb\rc\r\nd"), "a\r\nb\r\nc\r\nd")

    def test_idempotent(self):
        msg = b"Subject: x\r\n\r\nline\r\n.dot\r\n"
        self.assertEqual(normalize_eol(msg), msg)
        self.assertEqual(normalize_eol(normalize_eol(b"a\nb")), b"a\r\nb")

    def test_no_dot_stuffing(self):
        # dot-stuffing is smtplib's job: doing it here would double it
        self.assertEqual(normalize_eol(b".dot\n"), b".dot\r\n")
        self.assertEqual(smtplib._quote_periods(normalize_eol(b".dot\n")), b"..dot\r\n")

    def test_non_utf8_bytes_untouched(self):
        self.assertEqual(normalize_eol(b"\xe0\xe8\n"), b"\xe0\xe8\r\n")


class TestMailHostSend(unittest.TestCase):
    def setUp(self):
        self.mailhost = MailHost("MailHost")

    def send(self, message, **kwargs):
        with mock.patch("Products.MailHost.MailHost.DirectMailDelivery") as delivery:
            self.mailhost.send(message, **kwargs)
        return delivery.return_value.send.call_args[0][2]

    def test_message_object_is_sent_with_crlf(self):
        msg = MIMEMultipart()
        msg.attach(MIMEText("hello\n.class { color: red }\n", "html", "us-ascii"))
        sent = self.send(
            msg, mto="to@example.com", mfrom="from@example.com", subject="s"
        )
        self.assertIsNone(BARE_LF.search(sent))
        self.assertIn(b"\r\n\r\n", sent)
        # no extra dot added before smtplib's own dot-stuffing
        self.assertIn(b"\r\n.class { color: red }\r\n", sent)

    def test_string_message_unchanged(self):
        text = "From: from@example.com\nTo: to@example.com\nSubject: s\n\nbody\n"
        sent = self.send(text)
        self.assertIsNone(BARE_LF.search(sent))
        self.assertTrue(sent.endswith(b"\r\n\r\nbody\r\n"))

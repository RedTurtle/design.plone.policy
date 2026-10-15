# -*- coding: utf-8 -*-
"""Force RFC 5321 compliant CRLF line endings on outgoing emails.

Products.MailHost serializes the message with ``\\r\\n`` only when
``send()`` receives a string. When it receives an ``email.message.Message``
object (as many add-ons do, building ``MIMEText``/``MIMEMultipart``), the
message is serialized with the object's own policy (``compat32``, that uses
bare ``\\n``). ``smtplib.sendmail`` does not fix line endings for bytes
messages, so bare LFs reach the SMTP server.

After the "SMTP smuggling" mitigations (Postfix, Exchange/O365, ...) several
servers no longer accept a bare LF as a line terminator: the empty line that
separates headers and body is not recognized and the body ends up in the
headers.

Here we only normalize line endings, on bytes:

* no dot-stuffing: ``smtplib.SMTP.data`` already does it, doing it twice
  (e.g. with ``smtplib.quotedata``) would add a dot to every line starting
  with ``.``;
* no decode/encode: messages with 8bit non utf-8 content are left untouched;
* idempotent: an already compliant message is not modified.
"""

from Products.MailHost.MailHost import MailBase

import logging
import re

logger = logging.getLogger(__name__)

EOL_RE = re.compile(r"\r\n|\r(?!\n)|\n")
EOL_RE_BYTES = re.compile(rb"\r\n|\r(?!\n)|\n")


def normalize_eol(message):
    """Convert every line ending (``\\n``, ``\\r``, ``\\r\\n``) to ``\\r\\n``."""
    if isinstance(message, bytes):
        return EOL_RE_BYTES.sub(b"\r\n", message)
    if isinstance(message, str):
        return EOL_RE.sub("\r\n", message)
    return message


def apply():
    original_send = MailBase._send
    if getattr(original_send, "_design_plone_policy_crlf", False):
        return

    def _send(self, mfrom, mto, messageText, *args, **kwargs):
        return original_send(
            self, mfrom, mto, normalize_eol(messageText), *args, **kwargs
        )

    _send._design_plone_policy_crlf = True
    MailBase._send = _send
    logger.info("Patched Products.MailHost to always send CRLF line endings")

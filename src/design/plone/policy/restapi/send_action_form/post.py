# -*- coding: utf-8 -*-
from email.mime.text import MIMEText
from email.message import EmailMessage
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from smtplib import SMTPException
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides


class SendActionFormPost(Service):
    def reply(self):
        data = json_body(self.request)

        block_id = data.get("block_id", "")
        if not block_id:
            raise BadRequest("block_id mancante")

        block_data = self.get_block_data(block_id=block_id)
        if not block_data:
            raise BadRequest(
                'Blocco di tipo "form" con id "{}" non trovato'.format(  # noqa
                    block_id
                )
            )
        message = data.get("message", "")
        subject = data.get("subject", "") or block_data.get(
            "default_subject", ""
        )
        mfrom = data.get("from", "") or block_data.get("default_from", "")

        if not message or not subject or not mfrom:
            raise BadRequest(
                "Campo obbligatorio tra message, subject e from mancante".format(  # noqa
                    block_id
                ),
            )
        portal = api.portal.get()
        overview_controlpanel = getMultiAdapter(
            (portal, self.request), name="overview-controlpanel"
        )
        if overview_controlpanel.mailhost_warning():
            raise BadRequest("MailHost is not configured.")

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mto = block_data.get("to", mail_settings.email_from_address)
        encoding = registry.get("plone.email_charset", "utf-8")
        host = api.portal.get_tool(name="MailHost")

        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = mfrom
        msg["To"] = mto

        # with open("/Users/cekk/Desktop/mappa_ploni.pdf", "rb") as fp:
        #     data = fp.read()
        #     msg.add_attachment(
        #         data,
        #         maintype="application/pdf",
        #         subtype="application/pdf",
        #         filename="mappa_ploni.pdf",
        #     )

        msg["Reply-To"] = mfrom
        try:
            host.send(
                msg, charset=encoding,
            )

        except (SMTPException, RuntimeError):
            plone_utils = api.portal.get_tool(name="plone_utils")
            exception = plone_utils.exceptionString()
            message = "Unable to send mail: {}".format(exception)

            self.request.response.setStatus(500)
            return dict(
                error=dict(type="InternalServerError", message=message)
            )

        return self.reply_no_content()

    def get_block_data(self, block_id):
        blocks = getattr(self.context, "blocks", {})
        if not blocks:
            return {}
        for id, block in blocks.items():
            if id != block_id:
                continue
            block_type = block.get("@type", "")
            if block_type != "form":
                continue
            return block
        return {}

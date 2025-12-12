# -*- coding: utf-8 -*-
"""
We use this file to change the base behavior of collective.volto.formsupport
to support some new feature:
    - limit on form submit
    - unique field in one form

Why do we use monkeypatch instead of overriding the classes?
Because it's temporary, until collective.volto.formsupport can support backend
validation for data
"""
from collective.volto.formsupport import _
from collective.volto.formsupport.datamanager.catalog import FormDataStore
from collective.volto.formsupport.events import FormSubmittedEvent
from collective.volto.formsupport.interfaces import IFormDataStore
from collective.volto.formsupport.restapi.services.form_data.csv import (
    FormDataExportGet,
)
from collective.volto.formsupport.restapi.services.submit_form.post import logger
from collective.volto.formsupport.restapi.services.submit_form.post import (
    PostEventService,
)
from collective.volto.formsupport.restapi.services.submit_form.post import SubmitPost
from datetime import datetime
from io import StringIO
from plone.protect.interfaces import IDisableCSRFProtection
from plone import api
from souper.soup import Record
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import alsoProvides

import csv


SKIP_ATTRS = ["block_id", "fields_labels", "fields_order"]


def wrapper_get_data(orig):
    def get_data(self):
        res = orig(self)
        has_waiting_list = False
        if self.form_block.get("limit") is not None:
            limit = int(self.form_block["limit"])
            if limit > -1:
                has_waiting_list = True
        if has_waiting_list:
            reader = csv.DictReader(StringIO(res))
            columns = reader.fieldnames + ["waiting_list"]
            sbuf = StringIO()
            writer = csv.DictWriter(sbuf, fieldnames=columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for idx, row in enumerate(reader):
                if idx >= limit:
                    row["waiting_list"] = translate(_("yes_label", default="Yes"))
                else:
                    row["waiting_list"] = translate(_("no_label", default="No"))
                writer.writerow(row)
            res = sbuf.getvalue()
            sbuf.close()
            return res
        else:
            return res

    return get_data


def patch_FormDataExportGet_get_data():
    logger.info(
        "Patch collective.volto.formsupport.restapi.services.form_data.csv.FormDataExportGet.get_data "
        "addding waiting_list feature"
    )
    FormDataExportGet.get_data = wrapper_get_data(FormDataExportGet.get_data)


def reply(self):
    """
    This code is a copy of the original reply method from collective.volto.formsupport v3.2.2
    """
    if not self.block:
        # formsupport 3.3.0 compatibility
        from collective.volto.formsupport.interfaces import IPostAdapter

        self.form_data_adapter = getMultiAdapter(
            (self.context, self.request), IPostAdapter
        )
        self.form_data = self.get_form_data()
        # fix attachment fields
        if self.form_data.get("attachments"):
            for k, v in self.form_data["attachments"].items():
                if "field_id" not in v:
                    v["field_id"] = k
        self.block_id = self.form_data.get("block_id", "")
        if self.block_id:
            self.block = self.get_block_data(block_id=self.block_id)

    store_action = self.block.get("store", False)
    send_action = self.block.get("send", [])
    self.submit_limit = int(self.block.get("limit", "-1"))  # this is the patch

    # Disable CSRF protection
    alsoProvides(self.request, IDisableCSRFProtection)

    notify(PostEventService(self.context, self.form_data))

    if send_action or self.get_bcc():
        try:
            self.send_data()
        except BadRequest as e:
            raise e
        except Exception as e:
            logger.exception(e)
            message = translate(
                _(
                    "mail_send_exception",
                    default="Unable to send confirm email. Please retry later or contact site administrator.",
                ),
                context=self.request,
            )
            self.request.response.setStatus(500)
            return dict(type="InternalServerError", message=message)

    notify(FormSubmittedEvent(self.context, self.block, self.form_data))

    if store_action:
        self.store_data()

    # start patch - append waiting_list to response
    res = {"data": self.form_data.get("data", [])}
    waiting_list = (
        self.submit_limit is not None and -1 < self.submit_limit < self.count_data()
    )
    if waiting_list:
        res["waiting_list"] = waiting_list
    # end patch
    return res


def count_data(self):
    store = getMultiAdapter((self.context, self.request), IFormDataStore)
    return store.count()


# end patch


def patch_SubmitPost_reply():
    logger.info(
        "Patch reply method of class SubmitPost from collective.volto.formsupport"
    )
    SubmitPost.reply = reply
    SubmitPost.count_data = count_data


def add(self, data):
    form_fields = self.get_form_fields()
    if not form_fields:
        logger.error(
            'Block with id {} and type "form" not found in context: {}.'.format(
                self.block_id, self.context.absolute_url()
            )
        )
        return None

    fields = {
        f["field_id"]: {
            "label": f.get("custom_field_id", f.get("label", f["field_id"])),
            "type": f.get("field_type", "text"),
        }
        for f in form_fields
    }
    record = Record()
    fields_labels = {}
    fields_order = []
    fields_types = {}
    for field_data in data:
        field_id = field_data.get("field_id", "")
        value = field_data.get("value", "")
        if field_id in fields:
            field = fields[field_id]
            record.attrs[field_id] = self.storedValue(value, field["type"])
            fields_types[field_id] = field.get("type", "")
            fields_labels[field_id] = field["label"]
            fields_order.append(field_id)
        # else: skip the field
    record.attrs["fields_labels"] = fields_labels
    record.attrs["fields_order"] = fields_order
    record.attrs["fields_types"] = fields_types
    record.attrs["date"] = datetime.now()
    record.attrs["block_id"] = self.block_id

    # start patch
    keys = [(x["field_id"], x["label"]) for x in form_fields if x.get("unique", False)]
    if keys:
        saved_data = self.soup.data.values()
        for saved_record in saved_data:
            unique = False
            for key in keys:
                if record.attrs.storage[key[0]] != saved_record.attrs.storage.get(
                    key[0], None
                ):
                    unique = True
                    break

            if not unique:
                raise BadRequest(
                    api.portal.translate(
                        _(
                            "save_data_exception",
                            default='Unable to save data. These fields need to have an unique value:  "${fields}"',
                            mapping={"fields": ", ".join([x[1] for x in keys])},
                        )
                    )
                )
        # end patch

    return self.soup.add(record)


# start patch
def count(self, query=None):
    records = []
    if not query:
        records = self.soup.data.values()

    return len(records)


# end patch


def patch_FormDataStore_methods():
    logger.info(
        "Patch method add of FormDataStore class for collective.volto.formsupport"
    )
    FormDataStore.add = add
    logger.info(
        "Add method count of FormDataStore class for collective.volto.formsupport"
    )
    FormDataStore.count = count

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
from plone.restapi.serializer.converters import json_compatible
from souper.soup import Record
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import alsoProvides

import csv


SKIP_ATTRS = ["block_id", "fields_labels", "fields_order"]


def get_data(self):
    store = getMultiAdapter((self.context, self.request), IFormDataStore)
    sbuf = StringIO()
    fixed_columns = ["date"]
    columns = []
    # start patch
    custom_colums = []
    if self.form_block.get("limit", None) is not None:
        limit = int(self.form_block["limit"])
        if limit > -1:
            custom_colums.append("waiting_list")
    # end patch

    rows = []
    # start patch
    for index, item in enumerate(reversed(store.search())):
        # end patch
        data = {}
        fields_labels = item.attrs.get("fields_labels", {})
        for k in self.get_ordered_keys(item):
            if k in SKIP_ATTRS:
                continue
            value = item.attrs.get(k, None)
            label = fields_labels.get(k, k)
            if label not in columns and label not in fixed_columns:
                columns.append(label)
            data[label] = json_compatible(value)
        for k in fixed_columns:
            # add fixed columns values
            value = item.attrs.get(k, None)
            data[k] = json_compatible(value)

        # start patch
        if "waiting_list" in custom_colums:
            data.update(
                {
                    "waiting_list": (
                        translate(_("yes_label", default="Yes"))
                        if not (index < limit)
                        else translate(_("no_label", default="No"))
                    )
                }
            )
        # end patch

        rows.append(data)
    columns.extend(fixed_columns)
    columns.extend(custom_colums)
    writer = csv.DictWriter(sbuf, fieldnames=columns, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    res = sbuf.getvalue()
    sbuf.close()
    return res


def patch_FormDataExportGet_get_data():
    logger.info(
        "Patch get_data methos of class FormDataExporterGet from collective.volto.formsupport"  # noqa
    )
    FormDataExportGet.get_data = get_data


def reply(self):
    self.validate_form()

    # start patch
    self.store_action = self.block.get("store", False)
    self.send_action = self.block.get("send", [])
    self.submit_limit = int(self.block.get("limit", "-1"))

    # Disable CSRF protection
    alsoProvides(self.request, IDisableCSRFProtection)

    notify(PostEventService(self.context, self.form_data))
    data = self.form_data.get("data", [])
    # end patch

    if self.send_action:
        try:
            self.send_data()
        except BadRequest as e:
            raise e
        except Exception as e:
            logger.exception(e)
            message = translate(
                _(
                    "mail_send_exception",
                    default="Unable to send confirm email. Please retry later or contact site administrator.",  # noqa
                ),
                context=self.request,
            )
            self.request.response.setStatus(500)
            return dict(type="InternalServerError", message=message)
    # start patch
    if self.store_action:
        try:
            data = self.store_data()
        except ValueError as e:
            logger.exception(e)
            message = translate(
                _(
                    "save_data_exception",
                    default="Impossibile salvare i dati. I campi '${fields}' non sono univoci.",  # noqa
                    mapping={"fields": e.args[0]},
                ),
                context=self.request,
            )
            self.request.response.setStatus(500)
            return dict(type="InternalServerError", message=message)

    return {"data": data}
    # end patch


def store_data(self):
    store = getMultiAdapter((self.context, self.request), IFormDataStore)
    # start patch
    data = {"form_data": self.filter_parameters()}

    res = store.add(data=data)
    if not res:
        raise BadRequest("Unable to store data")

    waiting_list = (
        self.submit_limit is not None and -1 < self.submit_limit < self.count_data()
    )
    data.update({"waiting_list": waiting_list})

    return data


def count_data(self):
    store = getMultiAdapter((self.context, self.request), IFormDataStore)
    return store.count()


# end patch


def patch_SubmitPost_reply():
    logger.info(
        "Patch reply method of class SubmitPost from collective.volto.formsupport"
    )
    SubmitPost.reply = reply
    SubmitPost.store_data = store_data
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
        x["field_id"]: x.get("custom_field_id", x.get("label", x["field_id"]))
        for x in form_fields
    }
    record = Record()
    fields_labels = {}
    fields_order = []
    # start patch
    for field_data in data["form_data"]:
        # end patch
        field_id = field_data.get("field_id", "")
        value = field_data.get("value", "")
        if field_id in fields:
            record.attrs[field_id] = value
            fields_labels[field_id] = fields[field_id]
            fields_order.append(field_id)
    record.attrs["fields_labels"] = fields_labels
    record.attrs["fields_order"] = fields_order
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
                raise ValueError(f" {', '.join([x[1] for x in keys])}")
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

from design.plone.policy import _
from collective.volto.formsupport.interfaces import IFormDataStore
from collective.volto.formsupport.restapi.services.submit_form.post import (
    SubmitPost as BaseSubmitPost,
)
from plone import api
from zExceptions import BadRequest
from zope.component import getMultiAdapter


class SubmitPost(BaseSubmitPost):
    def reply(self):
        """
        Append waiting_list to response
        """
        res = super().reply()
        submit_limit = int(self.block.get("limit", "-1"))  # this is the patch
        waiting_list = (
            submit_limit is not None and -1 < submit_limit < self.count_data()
        )
        if waiting_list:
            res["waiting_list"] = waiting_list

        return res

    def count_data(self):
        """
        Return the number of submissions
        """
        store = getMultiAdapter((self.context, self.request), IFormDataStore)
        return store.length()

    def get_form_data(self):
        form_data = self.form_data_adapter()
        submitted_data = {x.get("field_id", ""): x for x in form_data.get("data", [])}
        # first
        store = getMultiAdapter((self.context, self.request), IFormDataStore)
        form_fields = store.get_form_fields()
        keys = [
            (x["field_id"], x.get("label", ""))
            for x in form_fields
            if x.get("unique", False)
        ]
        if keys:
            saved_data = store.soup.data.values()
            for saved_record in saved_data:
                for field_id, label in keys:
                    saved_value = saved_record.attrs.storage.get(field_id, None)
                    submit_value = submitted_data.get(field_id, {}).get("value", None)
                    if submit_value and submit_value == saved_value:
                        if label:
                            msg = api.portal.translate(
                                        _(
                                            "save_data_exception",
                                            default='Unable to save data. The value of field "${field}" is already stored in previous submissions.',
                                            mapping={"field": label},
                                        )
                                    )
                        else:
                            msg = api.portal.translate(
                                        _(
                                            "save_data_exception_no_label",
                                            default='Unable to save data. The value is already stored in previous submissions.',
                                        )
                                    )
                        raise BadRequest(
                            [
                                {
                                    "message": msg,
                                    "field_id": field_id,
                                    "label": label,
                                    "error": "UniqueValueError",
                                }
                            ]
                        )

        return form_data

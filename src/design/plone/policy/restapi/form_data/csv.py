from collective.volto.formsupport.restapi.services.form_data.csv import (
    FormDataExportGet as BaseFormDataExportGet,
)
from io import StringIO

import csv


class FormDataExportGet(BaseFormDataExportGet):
    def get_data(self):
        """
        Append waiting_list column to csv export
        """
        res = super().get_data()
        has_waiting_list = False
        if self.form_block.get("limit") is not None:
            limit = int(self.form_block["limit"])
            if limit > -1:
                has_waiting_list = True
        if not has_waiting_list:
            return res

        reader = csv.DictReader(StringIO(res))
        columns = list(reader.fieldnames)
        columns.insert(-1, "Lista d'attesa")
        sbuf = StringIO()
        writer = csv.DictWriter(sbuf, fieldnames=columns, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for idx, row in enumerate(reader):
            row["Lista d'attesa"] = idx >= limit and "Si" or "No"
            writer.writerow(row)
        res = sbuf.getvalue()
        sbuf.close()
        return res

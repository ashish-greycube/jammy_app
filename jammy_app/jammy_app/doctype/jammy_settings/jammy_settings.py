# -*- coding: utf-8 -*-
# Copyright (c) 2020, frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.csvutils import get_csv_content_from_google_sheets, read_csv_content
from frappe.utils import now, cstr, flt, nowtime
import hashlib
import csv
import json
import io


def to_csv(tsv_content):
    output = io.StringIO()

    tsv_reader = csv.reader(io.StringIO(tsv_content), delimiter='\t')
    csv_writer = csv.writer(output)

    for row in tsv_reader:
        csv_writer.writerow(row)

    return output.getvalue()


class JammySettings(Document):
    @frappe.whitelist()
    def import_amazon_csv(self):
        file_name = frappe.db.get_value("File", {"file_url": self.import_file})
        if not file_name:
            frappe.throw("CSV file not found %s" % self.import_file)
            return

        file_content = frappe.get_doc("File", file_name).get_content()
        csv_content = to_csv(file_content)
        rows = read_csv_content(csv_content)

        frappe.msgprint("Import %s rows" % (len(rows)-1), alert=True)

        orders = {}
        for d in rows[1:]:
            id = d[0]
            if not id in orders:
                orders[id] = [rows[0], d]
            else:
                if d[rows[0].index("order-status")] == "Cancelled":
                    continue
                orders[id].append(d)

        docs = []

        for oid, order in orders.items():
            if frappe.db.exists("Shipping Easy Order", {"external_order_identifier": oid}):
                print("%s exists" % oid)
                continue
            uid = hashlib.sha256(json.dumps(
                order).encode("utf-8")).hexdigest()
            try:
                doc = frappe.get_doc(
                    {
                        "doctype": "Shipping Easy Order",
                        "order_id": oid,
                        "external_order_identifier": oid,
                        "json_data": json.dumps(order),
                        "fetched_on": now(),
                        "status": "Pending",
                        "updated_at": order[1][order[0].index("last-updated-date")],
                        "uid": uid,
                    }
                ).insert(ignore_permissions=True)
                docs.append(doc)
            except frappe.exceptions.UniqueValidationError as ex:
                print("skiping uniq:", oid)

        frappe.db.commit()

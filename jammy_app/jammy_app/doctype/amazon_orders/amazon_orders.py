# Copyright (c) 2025, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.csvutils import read_csv_content
from frappe.utils import now

import io
import csv
import json
import hashlib


class AmazonOrders(Document):
    def get_val(self, row_idx, col, data):
        return data[row_idx][data[0].index(col)]

    @frappe.whitelist()
    def get_missing_orders(self):

        orders = []
        if self.amazon_file:
            file_doc = frappe.get_doc("File", {"file_url": self.amazon_file})
            if file_doc:
                orders = read_csv_content(to_csv(file_doc.get_content()))

                # set from to date
                if not self.from_date and len(orders) > 1:
                    col = 'last-updated-date'
                    self.db_set("from_date", self.get_val(2, col, orders))
                    self.db_set("to_date", self.get_val(-1, col, orders))
                    # self.notify_update()

                identifiers = ",".join([f"'{d[0]}'" for d in orders[1:]])
                invoices = frappe.db.sql("""
				select po_no from `tabSales Invoice`
				where docstatus = 1 and po_no in ({})""".format(identifiers,), pluck='po_no')
                orders = [d for d in orders if not d[0] in invoices]
        return orders

    @frappe.whitelist()
    def import_missing_orders(self):
        file_name = frappe.db.get_value("File", {"file_url": self.amazon_file})
        if not file_name:
            frappe.throw("CSV file not found %s" % self.amazon_file)
            return

        rows = self.get_missing_orders()

        orders = {}
        for d in rows[1:]:
            id = d[0]
            if not id in orders:
                orders[id] = [rows[0], d]
            else:
                if d[rows[0].index("order-status")] == "Cancelled":
                    continue
                orders[id].append(d)

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
            except frappe.exceptions.UniqueValidationError as ex:
                print("skiping uniq:", oid)

        frappe.db.commit()
        frappe.msgprint("Imported %d missing Orders." % len(orders))


def to_csv(tsv_content):
    output = io.StringIO()

    tsv_reader = csv.reader(io.StringIO(tsv_content), delimiter='\t')
    csv_writer = csv.writer(output)

    for row in tsv_reader:
        csv_writer.writerow(row)

    return output.getvalue()

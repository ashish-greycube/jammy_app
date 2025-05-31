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
from jammy_app.jammy_app.doctype.shipping_easy_order.shipping_easy_order import get_mapped_item, get_referral_discount_for_item


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
                orders[id].append(d)

        docs = []

        for oid, order in orders.items():
            if frappe.db.exists("Shipping Easy Order", {"external_order_identifier": oid}):
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

                # make_sales_invoice_from_csv(oid, order)
            except frappe.exceptions.UniqueValidationError as ex:
                print("skiping uniq:", oid)

        for d in docs:
            try:
                make_sales_invoice_from_csv(d)
            except Exception as e:
                frappe.log_error(title="Import AMAZON CSV: %s" %
                                 cstr(e), message=frappe.get_traceback())

        frappe.db.commit()


def get_val(row, col, header):
    return row[header.index(col)]


def make_sales_invoice_from_csv(doc):

    if frappe.db.get_value("Sales Invoice", {"po_no": doc.external_order_identifier}):
        return

    csv_data = json.loads(doc.json_data)

    header, items = csv_data[0], csv_data[1:]

    info = ""
    for i in ['ship-city', 'ship-state', 'ship-postal-code', 'ship-country']:
        info = info + cstr(get_val(items[0], i, header)) + ", "

    si = {
        "doctype": "Sales Invoice",
        "update_stock": 0,
        "posting_date": cstr(get_val(items[0], "last-updated-date", header))[:10],
        "set_posting_time": 1,
        "posting_time": nowtime(),
        "po_no": doc.external_order_identifier,
        "po_date": cstr(get_val(items[0], "purchase-date", header))[:10],
        "tracking_number": "",
        "ship_via": "",
        "email_option": "NO",
        "credit_card_fee": "NO",
        "company": "Jammy, Inc.",
        "cost_center": "Main - JI",
        "customer": "AMAZON.COM",
        "conversion_rate": 1,
        "currency": "USD",
        "custom_amazon_recipient_info": info.strip(", "),
        "items": []
    }
    for item in items:
        item_code = get_mapped_item(cstr(get_val(item, "sku", header)))
        item_defaults = frappe.db.get_value(
            "Item Default",
            {"parent": item_code},
            ["income_account", "expense_account"],
            as_dict=True,
        )
        si["items"].append({
            "item_code": item_code,
            "warehouse": 'FORT WORTH-BI - JI',
            "qty": int(cstr(get_val(item, "quantity", header))),
            "price_list_rate": flt(cstr(get_val(item, "item-price", header))),
            "base_price_list_rate": flt(cstr(get_val(item, "item-price", header))),
            "income_account": item_defaults and item_defaults.income_account,
            "expense_account": item_defaults and item_defaults.expense_account,
            "cost_center": 'Main - JI',
        })

    for item in si["items"]:
        if item["item_code"] == "Amazon Shipping Charge":
            continue
        referral_discount = get_referral_discount_for_item(item_code)
        if referral_discount:
            item["margin_type"] = None
            item["margin_rate_or_amount"] = None
            item["discount_percentage"] = referral_discount
            item["discount_account"] = "Amazon Fee - JI"

    for item in si["items"]:
        if item["item_code"] == "Amazon Shipping Charge":
            referral_discount = max(
                i.discount_percentage for i in si["items"])

    return frappe.get_doc(si).insert()

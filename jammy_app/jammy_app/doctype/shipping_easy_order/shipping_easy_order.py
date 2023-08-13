# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_datetime_str, add_days, today, get_datetime
import time
import hmac
import hashlib
import requests
import json

from erpnext import get_default_company
from frappe.utils import nowtime


class ShippingEasyOrder(Document):
    def on_update(self):
        frappe.enqueue_doc(
            self.doctype, self.name, "make_sales_invoice", queue="short", now=True
        )

    def make_sales_invoice(self):
        settings = frappe.get_single("Jammy Settings")

        si = frappe.new_doc("Sales Invoice")
        args = frappe._dict(json.loads(self.json_data))
        si.set_posting_time = 1
        si.posting_date = args["ordered_at"][:10]
        si.posting_time = nowtime()

        si.company = get_default_company()
        si.customer = settings.default_amazon_customer
        # si.debit_to = args.debit_to or "Debtors - _TC"
        si.update_stock = 1
        si.currency = settings.default_currency
        si.conversion_rate = args.conversion_rate or 1

        # si.is_return = args.is_return
        # si.return_against = args.return_against
        # si.cost_center = args.cost_center or "_Test Cost Center - _TC"

        for d in args["recipients"][0]["line_items"]:
            si.append(
                "items",
                {
                    "item_code": get_mapped_item(d["sku"]),
                    "warehouse": settings.default_amazon_warehouse,
                    "qty": d["quantity"],
                    "rate": d["unit_price"],
                    # "batch"
                    # "income_account": "Sales - _TC",
                    # "expense_account": "Cost of Goods Sold - _TC",
                    # "cost_center": args.cost_center or "_Test Cost Center - _TC",
                },
            )
        si.insert()


def get_mapped_item(sku):
    return frappe.db.get_value("Item", {"item_code": sku}, "name")


@frappe.whitelist()
def sync_orders(from_date=None):
    se_orders = fetch_orders(from_date)
    for d in json.loads(se_orders)["orders"]:
        doc = frappe.get_doc(
            {
                "doctype": "Shipping Easy Order",
                "order_id": d["id"],
                "external_order_identifier": d["external_order_identifier"],
                "json_data": json.dumps(d),
                "fetched_on": now(),
                "status": "Pending",
            }
        ).insert(ignore_permissions=True)
    frappe.db.commit()


def fetch_orders(from_date=None):
    # page
    # per_page max 200
    # last_updated_at = 2017-05-24T19:38:25Z
    # status = "shipped", "cleared", "pending_shipment", "ready_for_shipment"

    if not from_date:
        from_date = add_days(today(), -1)

    settings = frappe.get_single("Jammy Settings")

    api_timestamp = int(time.time())
    path = "/api/orders"

    params = frappe._dict()
    params["api_key"] = settings.shipping_easy_api_key
    params["api_timestamp"] = api_timestamp
    # params["last_updated_at"] = "2023-08-11T06%3A40%3A25Z"
    params["last_updated_at"] = "{}T00%3A00%3A00Z".format(add_days(today(), -1))
    params["per_page"] = 3
    params["status"] = "shipped"

    signature = generate_signature(
        settings.shipping_easy_api_secret, "GET", path, params
    )

    query = "&".join([f"{k}={v}" for k, v in params.items()])

    url = "{}{}?api_signature={}&{}".format(
        settings.shipping_easy_api_endpoint, path, signature, query
    )

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    return response.text


def generate_signature(hmac_secret, method, path, params):
    hmac_secret = str.encode(hmac_secret)
    params = frappe._dict(params)
    signing_string = "&".join([method, path] + [f"{k}={v}" for k, v in params.items()])

    hm = hmac.new(hmac_secret, signing_string.encode("utf-8"), hashlib.sha256)
    return hm.hexdigest()

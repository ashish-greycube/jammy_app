# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, flt, add_days, today, cint
import time
import hmac
import hashlib
import requests
import json
from erpnext import get_default_company, get_company_currency
from frappe.utils import nowtime
from erpnext.stock.doctype.batch.batch import UnableToSelectBatchError


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
        si.posting_date = args["shipments"][0]["ship_date"]
        si.posting_time = nowtime()
        si.po_no = args["external_order_identifier"]
        si.po_date = args["ordered_at"][:10]
        si.tracking_number = args["shipments"][0]["tracking_number"]
        si.ship_via = args["shipments"][0]["carrier_key"]

        si.email_option = "NO"
        si.credit_card_fee = "NO"

        si.company = get_default_company()
        si.customer = settings.default_amazon_customer
        si.update_stock = 1
        si.conversion_rate = args.conversion_rate or 1
        si.currency = frappe.db.get_value(
            "Customer", si.customer, "default_currency"
        ) or get_company_currency(si.company)

        # si.is_return = args.is_return
        # si.return_against = args.return_against
        # si.debit_to = args.debit_to or "Debtors - _TC"
        # si.cost_center = args.cost_center or "_Test Cost Center - _TC"

        for d in args["recipients"][0]["line_items"]:
            item_code = get_mapped_item(d["sku"])
            item_defaults = frappe.db.get_value(
                "Item Default",
                {"parent": item_code},
                ["income_account", "expense_account"],
                as_dict=True,
            )
            si.append(
                "items",
                {
                    "item_code": item_code,
                    "warehouse": settings.default_amazon_warehouse,
                    "qty": d["quantity"],
                    "rate": d["unit_price"],
                    "income_account": item_defaults and item_defaults.income_account,
                    "expense_account": item_defaults and item_defaults.expense_account
                    # "cost_center": args.cost_center or "_Test Cost Center - _TC",
                },
            )
        total_tax = args["total_tax"]
        if flt(total_tax):
            tax = {
                "charge_type": "Actual",
                "account_head": settings.taxes_account_head,
                "tax_amount": total_tax,
                "description": settings.taxes_account_head,
            }
            si.append("taxes", tax)
        try:
            si.insert()
            si.submit()
        except UnableToSelectBatchError:
            si.update_stock = 0
            si.insert()
            self.db_set("status", "Error")
        except Exception as ex:
            frappe.log_error(
                title="Sales Invoice from Shipping Easy Order failed.",
                message=frappe.get_traceback(),
                reference_doctype=self.doctype,
                reference_name=self.name,
            )
            self.db_set("status", "Error")

        self.db_set("status", "Processed")


def get_mapped_item(sku):
    return frappe.db.get_value("Item", {"item_code": sku}, "name")


@frappe.whitelist()
def sync_orders(from_date=None):
    se_orders = fetch_orders(from_date)
    for d in json.loads(se_orders)["orders"]:
        uid = hashlib.sha256(json.dumps(d).encode("utf-8")).hexdigest()
        try:
            doc = frappe.get_doc(
                {
                    "doctype": "Shipping Easy Order",
                    "order_id": d["id"],
                    "external_order_identifier": d["external_order_identifier"],
                    "json_data": json.dumps(d),
                    "fetched_on": now(),
                    "status": "Pending",
                    "uid": uid,
                }
            ).insert(ignore_permissions=True)
        except frappe.exceptions.UniqueValidationError as ex:
            print("skiping uniq:", d["external_order_identifier"])
            pass

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


def notify_errors():
    """Cron. Runs Daily to notify of Error status Orders."""
    orders = frappe.get_all("Shipping Easy Order", {"status": "Error"})
    if orders:
        if frappe.get_value("Notification", "Shipping Easy Failure Notification"):
            doc = frappe.get_doc("Shipping Easy Order", orders[0].name)
            frappe.get_doc(
                "Notification", "Shipping Easy Failure Notification"
            ).send_an_email(doc, {"count": len(orders)})

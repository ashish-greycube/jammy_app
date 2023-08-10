# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
import time
import hmac
import hashlib
import requests
import json


class ShippingEasyOrder(Document):
    def after_insert(self):
        # TODO: create sales invoice
        pass


@frappe.whitelist()
def sync_orders():
    se_orders = fetch_orders()
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


def fetch_orders():
    # page
    # per_page max 200
    # last_updated_at = 2017-05-24T19:38:25.000-00:00
    # status = "shipped", "cleared", "pending_shipment", "ready_for_shipment"

    settings = frappe.get_single("Jammy Settings")

    api_timestamp = int(time.time())
    path = "/api/orders"

    params = frappe._dict()
    params["api_key"] = settings.shipping_easy_api_key
    params["api_timestamp"] = api_timestamp

    signature = generate_signature(
        settings.shipping_easy_api_secret, "GET", path, params
    )

    headers = {"accept": "application/json"}
    url = "{}{}?api_key={}&api_signature={}&api_timestamp={}".format(
        settings.shipping_easy_api_endpoint,
        path,
        settings.shipping_easy_api_key,
        signature,
        api_timestamp,
    )
    response = requests.get(url, headers=headers)

    return response.text


def generate_signature(hmac_secret, method, path, params):
    hmac_secret = str.encode(hmac_secret)
    params = frappe._dict(params)
    signing_string = "&".join([method, path] + [f"{k}={v}" for k, v in params.items()])

    hm = hmac.new(hmac_secret, signing_string.encode("utf-8"), hashlib.sha256)
    return hm.hexdigest()

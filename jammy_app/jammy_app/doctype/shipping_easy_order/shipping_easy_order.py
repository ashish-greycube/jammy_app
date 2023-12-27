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
from erpnext import get_default_company, get_company_currency, get_default_cost_center
from frappe.utils import nowtime
from erpnext.stock.doctype.batch.batch import UnableToSelectBatchError


class ShippingEasyOrder(Document):
    def on_update(self):
        frappe.enqueue_doc(
            self.doctype, self.name, "make_sales_invoice", queue="short", now=True
        )

    def make_sales_invoice(self):
        try:
            if frappe.db.get_value(
                "Sales Invoice",
                {"po_no": self.external_order_identifier, "docstatus": 1},
            ):
                frappe.log_error(
                    title="Sales Invoice exists for po_no: %s. Skipping Shipping Easy Order: %s"
                    % (self.external_order_identifier, self.order_id)
                )

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
            si.cost_center = get_default_cost_center(si.company)
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

            si_items = []

            for d in args["recipients"][0]["line_items"]:
                item_code = get_mapped_item(d["sku"])
                item_defaults = frappe.db.get_value(
                    "Item Default",
                    {"parent": item_code},
                    ["income_account", "expense_account"],
                    as_dict=True,
                )

                item_args = {
                    "item_code": item_code,
                    "warehouse": settings.default_amazon_warehouse,
                    "qty": flt(d["quantity"]),
                    "price_list_rate": flt(d["unit_price"]),
                    "base_price_list_rate": flt(d["unit_price"]),
                    "income_account": item_defaults and item_defaults.income_account,
                    "expense_account": item_defaults and item_defaults.expense_account,
                    "cost_center": si.cost_center,
                }
                si_items.append(item_args)

            # add item for Shipping Cost
            base_shipping_cost = flt(args.get("base_shipping_cost", 0))
            if base_shipping_cost > 0:
                si_items.append(
                    {
                        "item_code": settings.shipping_charge_item,
                        "price_list_rate": base_shipping_cost,
                        "base_price_list_rate": base_shipping_cost,
                        "qty": 1,
                        "income_account": item_defaults
                        and item_defaults.income_account,
                        "expense_account": item_defaults
                        and item_defaults.expense_account,
                    },
                )

            # set Amazon Referral Fee
            # NOTE: The Shipping Fee will be correct only if Order has items with same Amazon Fee
            for d in si_items:
                if d["item_code"] == settings.shipping_charge_item:
                    referral_discount = max(i.discount_percentage for i in si.items)
                else:
                    referral_discount = get_referral_discount_for_item(item_code)

                if referral_discount:
                    d["margin_type"] = None
                    d["margin_rate_or_amount"] = None
                    d["discount_percentage"] = referral_discount
                    d["discount_account"] = settings.amazon_referral_discount_account
                si.append("items", d)

            # If Shipping cost needs to be added in taxes
            # base_shipping_cost = flt(args.get("base_shipping_cost", 0))
            # if base_shipping_cost > 0:
            #     si.append(
            #         "taxes",
            #         {
            #             "charge_type": "Actual",
            #             "account_head": settings.amazon_shipping_account,
            #             "tax_amount": base_shipping_cost,
            #             "description": "Shipping cost",
            #         },
            #     )

            # If needed to add Taxes. Skipping taxes currently as requested by Ralph.
            # total_tax = args["total_tax"]
            # if flt(total_tax):
            #     tax = {
            #         "charge_type": "Actual",
            #         "account_head": settings.taxes_account_head,
            #         "tax_amount": total_tax,
            #         "description": settings.taxes_account_head,
            #     }
            #     si.append("taxes", tax)

            si.insert()
            si.submit()
            self.db_set("status", "Processed")
        except UnableToSelectBatchError:
            # save as Draft only, do not Submit. User will need to submit after creating stock
            si.insert()
            self.db_set("status", "Processed")
        except Exception as e:
            frappe.log_error(e)
            self.db_set("status", "Error")


def get_mapped_item(sku):
    item_code = frappe.db.get_value("Item", {"item_code": sku}, "item_code")
    if not item_code:
        item_code = frappe.db.get_value("Item SKU Mapping", {"amazon_sku": sku}, "item")
    if not item_code:
        frappe.throw(f"Item not found: {sku}")
    return item_code


def get_referral_discount_for_item(item_code):
    out = frappe.db.sql(
        """
    with fn as
            (
            select t.amazon_referral_discount_pct_cf 
            from `tabItem Group` tig 
            inner join `tabItem Group` t on t.lft <= tig.lft and t.rgt >= tig.rgt 
            where tig.name = (select item_group from `tabItem` where item_code = %s)
            order by t.lft desc
            )
            select amazon_referral_discount_pct_cf
            from tabItem where item_code = %s 
                and amazon_referral_discount_pct_cf > 0
            union all
            select * from fn
            where amazon_referral_discount_pct_cf > 0 
            limit 1
                        """,
        (item_code, item_code),
    )
    return out and flt(out[0][0])


@frappe.whitelist()
def sync_orders(from_date=None, order_id=None):
    if not cint(frappe.db.get_single_value("Jammy Settings", "is_syncing_enabled")):
        frappe.throw("Please enable syncing in Jammy Settings")
    se_orders = fetch_orders(from_date)
    for d in json.loads(se_orders)["orders"]:
        make_shipping_easy_order(d)


def make_shipping_easy_order(order):
    uid = hashlib.sha256(json.dumps(order).encode("utf-8")).hexdigest()
    try:
        doc = frappe.get_doc(
            {
                "doctype": "Shipping Easy Order",
                "order_id": order["id"],
                "external_order_identifier": order["external_order_identifier"],
                "json_data": json.dumps(order),
                "fetched_on": now(),
                "status": "Pending",
                "uid": uid,
            }
        ).insert(ignore_permissions=True)
    except frappe.exceptions.UniqueValidationError as ex:
        print("skiping uniq:", order["external_order_identifier"])
        pass

    frappe.db.commit()


@frappe.whitelist()
def fetch_order(order_id="3415852983"):
    api_timestamp = int(time.time())
    path = f"/api/orders/{order_id}"
    settings = frappe.get_single("Jammy Settings")

    params = frappe._dict()
    params["api_key"] = settings.shipping_easy_api_key
    params["api_timestamp"] = api_timestamp
    signature = generate_signature(
        settings.shipping_easy_api_secret, "GET", path, params
    )

    query = "&".join([f"{k}={v}" for k, v in params.items()])

    url = "{}{}?api_signature={}&{}".format(
        settings.shipping_easy_api_endpoint, path, signature, query
    )

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    # return response.text
    make_shipping_easy_order(json.loads(response.text)["order"])


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
    params["last_updated_at"] = "{}T00%3A00%3A00Z".format(from_date)
    # params["per_page"] = 3
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

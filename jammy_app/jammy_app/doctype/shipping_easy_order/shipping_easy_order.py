# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, flt, add_days, today, cint, cstr
import json
from erpnext import get_default_company, get_company_currency, get_default_cost_center
from frappe.utils import nowtime
from erpnext.stock.doctype.batch.batch import UnableToSelectBatchError
import erpnext


class ShippingEasyOrder(Document):
    def on_update(self):
        sales_invoice = None

        try:
            if self.order_id == self.external_order_identifier:
                sales_invoice = self.make_sales_invoice_from_csv()
                # Cancelled
                data = json.loads(self.json_data)
                order_status_index = data[0].index("order-status")
                if not any(row[order_status_index] != "Cancelled" for row in data[1:]):
                    self.db_set("status", "Cancelled")
                    return
            else:
                sales_invoice = self.make_sales_invoice()
        except Exception as e:
            self.set_error("Error")

        if sales_invoice:
            try:
                sales_invoice.update_stock = 1
                sales_invoice.save()
                sales_invoice.submit()
            except erpnext.stock.stock_ledger.NegativeStockError:
                self.set_error("Error")
            except UnableToSelectBatchError:
                self.set_error("Batch Error")
            except Exception as e:
                self.set_error("Error")

    def set_error(self, status):
        self.db_set(
            {"status": status, "error": frappe.get_traceback(with_context=True)})

    def get_recipient_info(self):
        template = """
    {{first_name or ""}} {{last_name or ""}}
    {{address or ""}}, {{address2 or ""}}, {{address3 or ""}}
    {{city or ""}}, {{state or ""}}, {{country or ""}}, {{postal_code or ""}}
    {{phone_number or ""}} {{email or ""}}
    """

        data = dict(json.loads(self.json_data))
        for d in data.get("recipients", []):
            if d.get("first_name") == "[REDACTED]":
                continue
            info = frappe.render_template(template, d)
            return info
        return "[REDACTED]"

    def make_sales_invoice(self):
        if frappe.db.get_value(
            "Sales Invoice",
            {"po_no": self.external_order_identifier, "docstatus": 1},
        ):
            frappe.log_error(
                title="Sales Invoice exists for po_no: %s. Skipping Shipping Easy Order: %s"
                % (self.external_order_identifier, self.order_id)
            )
            return

        settings = frappe.get_single("Jammy Settings")

        sales_invoice = frappe.new_doc("Sales Invoice")
        args = frappe._dict(json.loads(self.json_data))

        # set update_stock to 1 after Draft is saved, to avoid UnableToSelectBatchError
        sales_invoice.update_stock = 0

        sales_invoice.posting_date = args["shipments"][0]["ship_date"]
        sales_invoice.set_posting_time = 1
        sales_invoice.posting_time = nowtime()
        sales_invoice.po_no = args["external_order_identifier"]
        sales_invoice.po_date = args["ordered_at"][:10]
        sales_invoice.tracking_number = args["shipments"][0]["tracking_number"]
        sales_invoice.ship_via = args["shipments"][0]["carrier_key"]

        sales_invoice.email_option = "NO"
        sales_invoice.credit_card_fee = "NO"

        sales_invoice.company = get_default_company()
        sales_invoice.cost_center = get_default_cost_center(
            sales_invoice.company)
        sales_invoice.customer = settings.default_amazon_customer
        sales_invoice.conversion_rate = args.conversion_rate or 1
        sales_invoice.currency = frappe.db.get_value(
            "Customer", sales_invoice.customer, "default_currency"
        ) or get_company_currency(sales_invoice.company)

        # si.is_return = args.is_return
        # si.return_against = args.return_against
        # si.debit_to = args.debit_to or "Debtors - _TC"
        # si.cost_center = args.cost_center or "_Test Cost Center - _TC"

        sales_invoice.custom_amazon_recipient_info = self.get_recipient_info()

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
                "cost_center": sales_invoice.cost_center,
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
                referral_discount = max(
                    i.discount_percentage for i in sales_invoice.items)
            else:
                referral_discount = get_referral_discount_for_item(
                    item_code)

            if referral_discount:
                d["margin_type"] = None
                d["margin_rate_or_amount"] = None
                d["discount_percentage"] = referral_discount
                d["discount_account"] = settings.amazon_referral_discount_account
            sales_invoice.append("items", d)

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

        if sales_invoice.items:
            sales_invoice.insert()
        return sales_invoice

    @frappe.whitelist()
    def make_sales_invoice_from_csv(self):

        if frappe.db.get_value("Sales Invoice", {"po_no": self.external_order_identifier, "docstatus": 1}):
            return

        csv_data = json.loads(self.json_data)

        header, items = csv_data[0], csv_data[1:]

        info = ""
        for i in ['ship-city', 'ship-state', 'ship-postal-code', 'ship-country']:
            info = info + cstr(self.get_val(items[0], i, header)) + ", "

        si = {
            "doctype": "Sales Invoice",
            "update_stock": 0,
            "posting_date": cstr(self.get_val(items[0], "last-updated-date", header))[:10],
            "set_posting_time": 1,
            "posting_time": nowtime(),
            "po_no": self.external_order_identifier,
            "po_date": cstr(self.get_val(items[0], "purchase-date", header))[:10],
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
            if cstr(self.get_val(item, "order-status", header)) == "Cancelled":
                continue

            item_code = get_mapped_item(
                cstr(self.get_val(item, "sku", header)))
            item_defaults = frappe.db.get_value(
                "Item Default",
                {"parent": item_code},
                ["income_account", "expense_account"],
                as_dict=True,
            )
            qty = int(cstr(self.get_val(item, "quantity", header)))
            if not qty:
                continue
            referral_discount = get_referral_discount_for_item(item_code)

            price_list_rate = flt(
                cstr(self.get_val(item, "item-price", header)))/qty

            if referral_discount:
                price_list_rate = price_list_rate/(1-referral_discount*.01)

            si["items"].append({
                "item_code": item_code,
                "warehouse": 'FORT WORTH-BI - JI',
                "qty": int(cstr(self.get_val(item, "quantity", header))),
                "price_list_rate": price_list_rate,
                "base_price_list_rate": price_list_rate,
                "income_account": item_defaults and item_defaults.income_account,
                "expense_account": item_defaults and item_defaults.expense_account,
                "cost_center": 'Main - JI',
            })

            # add shipping item
            item_defaults = frappe.db.get_value(
                "Item Default",
                {"parent": "Amazon Shipping Charge"},
                ["income_account", "expense_account"],
                as_dict=True,
            )

            if shipping_price := cstr(self.get_val(item, "shipping-price", header)):
                si["items"].append({
                    "item_code": "Amazon Shipping Charge",
                    "warehouse": 'FORT WORTH-BI - JI',
                    "qty": 1,
                    "price_list_rate": shipping_price,
                    "base_price_list_rate": shipping_price,
                    "income_account": item_defaults and item_defaults.income_account,
                    "expense_account": item_defaults and item_defaults.expense_account,
                    "cost_center": 'Main - JI',
                })

        for item in si["items"]:
            if item["item_code"] == "Amazon Shipping Charge":
                continue
            if referral_discount:
                item["margin_type"] = None
                item["margin_rate_or_amount"] = None
                item["discount_percentage"] = referral_discount
                item["discount_account"] = "Amazon Fee - JI"

        for item in si["items"]:
            if item["item_code"] == "Amazon Shipping Charge":
                referral_discount = max(
                    flt(i.get("discount_percentage")) for i in si["items"])

        if not si["items"]:
            return

        sales_invoice = frappe.get_doc(si)
        sales_invoice.insert()

        return sales_invoice

    def get_val(self, row, col, header):
        return row[header.index(col)]


def get_mapped_item(sku):
    item_code = frappe.db.get_value("Item", {"item_code": sku}, "item_code")
    if not item_code:
        item_code = frappe.db.get_value(
            "Item SKU Mapping", {"amazon_sku": sku}, "item")
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


def on_submit_sales_invoice(doc, method):
    seo_name = frappe.db.get_value('Shipping Easy Order', {
                                   'external_order_identifier': doc.po_no})
    if seo_name:
        frappe.db.set_value('Shipping Easy Order',
                            seo_name, "status", "Processed")

import frappe
from frappe.utils import now, cint
import json


@frappe.whitelist(allow_guest=True)
def shipment(**args):
    """
    Not used currently as it works only for orders created through api (not amazon store orders)
    Post to /api/method/jammy_app.shipping_easy.shipment
    https://shippingeasy.readme.io/reference/shipment-notification-callback
    """
    if not cint(
        frappe.db.get_single_value("Jammy Settings", "enable_shipment_callback")
    ):
        return

    # TODO: authorize and validate payload with secret_key
    if "cmd" in args:
        args.pop("cmd")

    if args.get("shipment"):
        doc = frappe.get_doc(
            {
                "doctype": "Shipping Easy Order",
                "json_data": json.dumps(args.get("shipment")),
                "fetched_on": now(),
                "status": "Pending",
            }
        ).insert(ignore_permissions=True)
        return doc.name

    frappe.log_error(title="Easy Shipping Callback", message=args)
    return "received shipment"

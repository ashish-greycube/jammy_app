import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    print("Creating Get Outstanding Invoice in Payment Entry...")
    custom_fields = {
        "Payment Entry": [
            dict(
                fieldname="get_outstanding_invoice_cf",
                label="Get Outstanding Invoice",
                fieldtype="Button",
                depends_on="eval:doc.docstatus==0",
                insert_after="get_outstanding_invoice",
            )
        ]
    }

    create_custom_fields(custom_fields, update=True)
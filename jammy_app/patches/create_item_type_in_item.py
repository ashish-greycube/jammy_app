import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    print("Creating Item Type in Item...")
    custom_fields = {
        "Item": [
            dict(
                fieldname="item_type_cf",
                label="Item type",
                fieldtype="Select",
                options="Routine Order\nSpecial Order",
                default="Routine Order",
                insert_after="notes",
                translatable=0
            )
        ]
    }

    create_custom_fields(custom_fields, update=True)
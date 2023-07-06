import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Item Group": [
            dict(
                fieldname="nmfc_cf",
                label="NMFC",
                fieldtype="Int",
                insert_after="column_break_5",
            ),
            dict(
                fieldname="freight_class_cf",
                label="Freight Class",
                fieldtype="Link",
                options="Freight Class JI",
                insert_after="nmfc_cf",
            ),  
        ]   
    }

    create_custom_fields(custom_fields, update=True)
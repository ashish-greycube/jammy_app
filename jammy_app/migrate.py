import frappe
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
    if not frappe.get_value("Notification", "Shipping Easy Failure Notification"):
        print("jammy_app: creating Shipping Easy Failure Notification notification")
        make_records(
            [
                {
                    "doctype": "Notification",
                    "name": "Shipping Easy Failure Notification",
                    "subject": "Please resolve Shipping Easy Orders that failed.",
                    "document_type": "Shipping Easy Order",
                    "event": "Custom",
                    "message": "{{count}} Shipping Easy Orders have failed. Please resolve the Orders manually and set Status as 'Processed'.",
                    "recipients": [{"receiver_by_role": "Administrator"}],
                }
            ]
        )
    setup_custom_fields()


def setup_custom_fields():
    custom_fields = {
        "Item Group": [
            dict(
                fieldname="amazon_referral_discount_pct_cf",
                label="Amazon Referral Discount %",
                fieldtype="Percent",
                insert_after="freight_class_cf",
                print_hide=1,
            )
        ],
    }

    create_custom_fields(custom_fields, update=True)

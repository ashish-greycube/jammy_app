import frappe
from frappe.desk.page.setup_wizard.setup_wizard import make_records


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

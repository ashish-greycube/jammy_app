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
    create_custom_fields_for_tariff()


def setup_custom_fields():
    custom_fields = {
        "Item Group": [
            dict(
                fieldname="amazon_referral_discount_pct_cf",
                label="Amazon Referral Fee %",
                fieldtype="Percent",
                insert_after="freight_class_cf",
                print_hide=1,
            )
        ],
        "Item": [
            dict(
                fieldname="amazon_referral_discount_pct_cf",
                label="Amazon Referral Fee %",
                fieldtype="Percent",
                insert_after="include_item_in_manufacturing",
                print_hide=1,
            )
        ],
    }

    create_custom_fields(custom_fields, update=True)


def create_custom_fields_for_tariff():
	custom_fields = {
		"Customer": [
			dict(
				fieldname="custom_apply_tariff",
				label="Apply Tariff?",
				fieldtype="Check",
				insert_after="image",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=1
			),
		],
        "Batch": [
			dict(
				fieldname="custom_tariff_recovery",
				label="Tariff Recovery %",
				fieldtype="Percent",
				insert_after="description",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=1
			),
		],
        
		###### Sales Order ######
        "Sales Order": [
              dict(
				fieldname="custom_apply_tariff",
				label="Apply Tariff?",
				fieldtype="Check",
				insert_after="delivery_date",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=0
			),
			dict(
				fieldname="custom_dt_tariff_amount",
				label="DT Tariff Amount",
				fieldtype="Currency",
				insert_after="column_break_46",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=0,
				read_only=1,
			),
		],
            
		###### Sales Order Item ######
        "Sales Order Item": [
              dict(
				fieldname="custom_tariff_recovery",
				label="Tariff Recovery %",
				fieldtype="Percent",
				insert_after="batch_no",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=0,
                fetch_from="batch_no.custom_tariff_recovery",
                read_only=1,
			),
			dict(
				fieldname="custom_tariff_rate",
				label="Tariff Rate",
				fieldtype="Currency",
				insert_after="amount",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=0,
				read_only=1,
			),
			dict(
				fieldname="custom_tariff_amount",
				label="Tariff Amount",
				fieldtype="Currency",
				insert_after="custom_tariff_rate",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=0,
				read_only=1,
			),
		],
            
		###### Sales Invoice ######
        
		"Sales Invoice": [
              dict(
				fieldname="custom_apply_tariff",
				label="Apply Tariff?",
				fieldtype="Check",
				insert_after="tax_id",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=0
			),
			dict(
				fieldname="custom_dt_tariff_amount",
				label="DT Tariff Amount",
				fieldtype="Currency",
				insert_after="column_break_47",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=1,
				read_only=1,
			),
		],
            
		"Sales Invoice Item": [
              dict(
				fieldname="custom_tariff_recovery",
				label="Tariff Recovery %",
				fieldtype="Percent",
				insert_after="batch_no",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=1,
                fetch_from="batch_no.custom_tariff_recovery",
                read_only=1,
			),
			dict(
				fieldname="custom_tariff_rate",
				label="Tariff Rate",
				fieldtype="Currency",
				insert_after="amount",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=1,
				read_only=1,
			),
			dict(
				fieldname="custom_tariff_amount",
				label="Tariff Amount",
				fieldtype="Currency",
				insert_after="custom_tariff_rate",
				is_custom_field=1,
				is_system_generated=0,
				translatable=0,
				no_copy=1,
				read_only=1,
			),
		],
        
	}

	print("Creating custom fields for Jammy app:")
	for dt, fields in custom_fields.items():
		print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
	create_custom_fields(custom_fields)
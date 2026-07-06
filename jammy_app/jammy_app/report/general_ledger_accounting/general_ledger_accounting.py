# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.general_ledger.general_ledger import execute as gl_execute

def execute(filters=None):
    # 1. Call the standard General Ledger execute function
    print("Executing General Ledger Accounting Report with filters:", filters)
    columns, data = gl_execute(filters)
    
    if not data:
        return columns, data

    # 2. Add your 2 new custom columns
    # IMPORTANT: Changed fieldtype to 'Data' so inserting "ADV" text doesn't cause a Link error
    new_columns = [
        {
            "label": _("Payment ID"),
            "fieldname": "payment_id",
            "fieldtype": "Link",
            "options": "Payment Entry", 
            "width": 120
        },
        {
            "label": _("Payment Reference"),
            "fieldname": "payment_reference",
            "fieldtype": "Data",
            "width": 120
        }
    ]
    
    insert_index = next((i + 1 for i, col in enumerate(columns) if col.get("fieldname") == "cost_center"), len(columns))
    for col in reversed(new_columns):
        columns.insert(insert_index, col)

    # 3. Bulk fetch Payment Details to keep the report fast
    vouchers = [row.get("voucher_no") for row in data if isinstance(row, dict) and row.get("voucher_no")]
    payment_map = {}
    
    if vouchers:
        # Fetch matching payment entries all at once
        # Note: Ensure 'reference' matches the exact database fieldname of your custom reference column
        payments = frappe.get_all(
            "Payment Entry Reference", 
            filters={"reference_name": ("in", vouchers), "docstatus": 1},
            fields=["reference_name", "parent", "custom_supplier_delivery_note as payment_reference"] 
        )
        for p in payments:
            payment_map[p.reference_name] = p

    # 4. Process each row to map payments and inject "ADV" if empty
    fields_to_check = [
        "voucher_no", 
        "payment_id", 
        "payment_reference", 
        "against_voucher"
    ]

    updated_data = []
    for row in data:
        if isinstance(row, dict):
            # Check for total/summary rows which shouldn't be tagged as (ADV)
            is_summary_row = row.get("bold") or "Total" in str(row.get("voucher_no", "")) or not row.get("posting_date")
            
            if not is_summary_row:
                v_no = row.get("voucher_no")
                
                # Assign actual values from the payment map if they exist
                if v_no and v_no in payment_map:
                    row["payment_id"] = payment_map[v_no].parent
                    row["payment_reference"] = payment_map[v_no].payment_reference

                # If any field in fields_to_check is empty/None, substitute with "ADV"
                for field in fields_to_check:
                    if not row.get(field):
                        row[field] = "ADV"
            else:
                # Provide empty values for summary rows so the layout aligns
                row["payment_id"] = ""
                row["payment_reference"] = ""
                
            updated_data.append(row)
        else:
            updated_data.append(row)

    return columns, updated_data
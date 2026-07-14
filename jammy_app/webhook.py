import frappe

@frappe.whitelist(allow_guest=True)
def on_payment_authorized():
    """
    This function is called when a payment is authorized.
    It can be used to perform actions such as updating the order status.
    """
    data = frappe.local.form_dict

    if data:
        try:
            status = data.get("status")
            isPaid = data.get("paid")
            if status == "succeeded" and isPaid:
                description = data.get("description")
                payment_req = frappe.get_doc("Payment Request", {"subject": description}, "name")
                if payment_req:
                    reference_doctype = frappe.db.set_value("Payment Request", payment_req, 'reference_doctype')
                    reference_name = frappe.db.set_value("Payment Request", payment_req, 'reference_name')
                    payment_entry = create_payment_entry(reference_doctype, reference_name, data)
                    if payment_entry:
                        frappe.db.set_value("Payment Request", payment_req, "status", "Paid")
                        frappe.db.commit()
                    return
        except Exception as e:
            log = frappe.log_error(message=frappe.get_traceback(), title="Stripe: Payment Authorization Error for")
            return
    else:
        log = frappe.log_error(message=data, title="Stripe: No Response Data From Webhook")
        return

def create_payment_entry(reference_doctype, reference_name, data):
    """
    This function creates a payment entry in the system.
    """
    try:
        reference_doc = frappe.get_doc(reference_doctype, reference_name)
        settings = frappe.get_doc("Jammy Settings")
        payment_entry = frappe.new_doc("Payment Entry")

        payment_entry.update({
            'payment_type' : 'Receive',
            'mode_of_payment' : 'Credit Card',
            'posting_date' : frappe.utils.today(),
            'party_type': 'Customer',
            'party' : reference_doc.customer,
            'paid_from' : settings.default_paid_from_account,
            'paid_to' : settings.default_paid_to_account,
            'paid_amount' : data.get('amount') / 100,
            'reference_no' : reference_name,
            'reference_date' : frappe.utils.today(),
        })

        payment_entry.insert(ignore_permissions=True)
        return payment_entry.name
    except Exception as e:
        log = frappe.log_error(message=frappe.get_traceback(), title="Stripe: Payment Entry Creation Error")
        return
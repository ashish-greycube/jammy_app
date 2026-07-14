import frappe
import stripe

@frappe.whitelist(allow_guest=True)
def on_payment_authorized():
    """
    Webhook endpoint to handle successful Stripe charge payments.
    """
    # 1. Setup Keys
    stripe_settings = frappe.get_doc("Stripe Settings", "Stripe Gateway")
    jammy_settings = frappe.get_doc("Jammy Settings")
    stripe.api_key = stripe_settings.get_password("secret_key")
    endpoint_secret = jammy_settings.get_password("stripe_webhook_secret")

    # 2. Get Raw Payload
    payload = frappe.request.get_data(as_text=True)
    sig_header = frappe.request.headers.get('Stripe-Signature')

    event = None

    # 3. Verify Signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Meaningful title for malformed JSON/Data
        frappe.log_error(message=str(e), title="Stripe Webhook Error: Invalid JSON Payload")
        frappe.local.response['http_status_code'] = 400
        return "Invalid payload"
    except stripe.error.SignatureVerificationError as e:
        # Meaningful title for security/hacker attempts
        frappe.log_error(message=str(e), title="Stripe Webhook Security: Signature Verification Failed")
        frappe.local.response['http_status_code'] = 400
        return "Invalid signature"

    # 4. Handle the 'charge.succeeded' event
    # Stripe wraps the payload you provided inside an event object
    if event['type'] == 'charge.succeeded':
        
        # This 'charge' variable now contains the exact JSON payload you shared above
        charge = event['data']['object'] 
        
        description = charge.get("description")
        status = charge.get("status")
        is_paid = charge.get("paid")
        
        # Double check the status based on your payload flags
        if status == "succeeded" and is_paid:
            try:
                # Find the Payment Request name where subject == description
                payment_req_name = frappe.db.get_value("Payment Request", {"subject": description}, "name")
                
                if payment_req_name:
                    ref_doctype, ref_name = frappe.db.get_value(
                        "Payment Request", 
                        payment_req_name, 
                        ['reference_doctype', 'reference_name']
                    )
                    
                    # Pass the charge object to your entry creation function
                    payment_entry = create_payment_entry(ref_doctype, ref_name, charge)
                    
                    if payment_entry:
                        frappe.db.set_value("Payment Request", payment_req_name, "status", "Paid")
                        frappe.db.commit()
                else:
                    # Meaningful title for missing records. Includes Charge ID for easy debugging.
                    frappe.log_error(
                        message=f"Could not find a Payment Request with subject: '{description}'. Charge ID: {charge.get('id')}", 
                        title="Stripe Webhook Mismatch: Payment Request Not Found"
                    )
                    
            except Exception as e:
                # Meaningful title for database/code crashes. Includes Charge ID.
                frappe.log_error(
                    message=frappe.get_traceback(), 
                    title=f"Stripe Webhook Critical: DB Update Failed for Charge {charge.get('id')}"
                )
                frappe.local.response['http_status_code'] = 500
                return "Internal Server Error"

    # 5. Always return a 200 OK to Stripe
    frappe.local.response['http_status_code'] = 200
    return "Success"

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
import frappe

@frappe.whitelist()
def get_freight_and_tariff(invoices):
    default_tariff, default_freight = frappe.db.get_value(
        doctype = 'Tariff Recovery Settings JI',
        fieldname = ['tariff_recovery_account', 'default_sales_freight_account']
    )
    
    invoices = invoices.split(",")
    tax_list = []
   
    if len(invoices) > 0:
        for invoice in invoices:
            if frappe.db.exists("Sales Invoice", invoice):
                si_doc = frappe.get_doc("Sales Invoice", invoice)
            
                if len(si_doc.taxes) > 0:
                    tax_dict = {
                        "sales_invoice" : invoice
                    }
                    for tax in si_doc.taxes:
                        if tax.account_head == default_tariff:
                            tax_dict["tariff_value"] = tax.tax_amount
                        
                        elif tax.account_head == default_freight:
                            tax_dict["freight_value"] = tax.tax_amount
                            
                    tax_list.append(tax_dict)
    return tax_list
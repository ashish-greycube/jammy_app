// Copyright (c) 2023, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bill Of Lading JI', {
    freight_charge_terms: function(frm) {
        if (frm.doc.freight_charge_terms == 'Prepaid') {
            frappe.db.get_single_value('Bill Of Lading Settings JI', 'company_address')
                .then(company_address_display => {
                    frm.set_value('third_party_freight_charges_bill_to', company_address_display);
                })
        } 
		else if(frm.doc.freight_charge_terms == 'Collect'){
			frappe.db.get_value('Delivery Note', frm.doc.ref, 'shipping_address', function(response) {
                frm.set_value('third_party_freight_charges_bill_to', response.shipping_address);
            });
		}
		else{
			frm.set_value('third_party_freight_charges_bill_to', " ");
		}
    }
});


// Copyright (c) 2023, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bill Of Lading JI', {
    freight_charge_terms_prepaid_unless_marked_otherwise: function(frm) {
        if (frm.doc.freight_charge_terms_prepaid_unless_marked_otherwise == 'Prepaid') {
            frappe.model.get_value('Delivery Note', frm.doc.ref, 'address_display', function(response) {
                frm.set_value('third_party_freight_charges_bill_to', response.address_display);
            });
        } 
		else if(frm.doc.freight_charge_terms_prepaid_unless_marked_otherwise == 'Collect'){
			frappe.db.get_value('Delivery Note', frm.doc.ref, 'shipping_address', function(response) {
                frm.set_value('third_party_freight_charges_bill_to', response.shipping_address);
            });
		}
		else{
			frm.set_value('third_party_freight_charges_bill_to', " ");
		}
    }
});


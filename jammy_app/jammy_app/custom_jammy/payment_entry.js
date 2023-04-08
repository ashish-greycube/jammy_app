cur_frm.add_fetch('party','default_sales_partner','sales_partner');


frappe.ui.form.on('Payment Entry Reference', {
	refresh(frm) {
		cur_frm.add_fetch('reference_name','total_taxes_and_charges','freight_charges');
		cur_frm.add_fetch('reference_name','base_total_taxes_and_charges','freight_charges');
	}
})
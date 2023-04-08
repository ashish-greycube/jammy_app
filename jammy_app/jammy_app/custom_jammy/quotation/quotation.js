frappe.ui.form.on('Quotation',{
	refresh:function(frm){
		frappe.db.get_value('Terms and Conditions', {'is_default': 1}, 'name', (r) => {
				frm.set_value('tc_name', r.name);
			});
	}
});

// cur_frm.add_fetch('customer','credit_days_based_on','credit_days_based_on');
// cur_frm.add_fetch('customer','credit_days','credit_days');
// cur_frm.add_fetch('customer','credit_limit','credit_limit');
cur_frm.add_fetch('customer','payment_terms','payment_terms');
cur_frm.add_fetch('customer','freight_ppd','freight_ppd');
cur_frm.add_fetch('customer','shipping_account','shipping_account');

cur_frm.add_fetch('item_code', 'net_weight', 'net_weight');
cur_frm.add_fetch('item_code', 'pcs_ctn', 'pcs_ctn');

frappe.ui.form.on("Quotation Item", "qty", function(frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
	set_gross_weight(frm, cdt, cdn);
	set_total_cartons(frm);
	set_total_weight(frm);
});
frappe.ui.form.on("Quotation Item", "net_weight", function(frm, cdt, cdn) {
	set_gross_weight(frm, cdt, cdn);
	set_total_weight(frm);
});
frappe.ui.form.on("Quotation Item", "pcs_ctn", function(frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
	set_total_cartons(frm);
});

frappe.ui.form.on("Quotation Item", "cartons", function(frm) {
	set_total_cartons(frm);
});
frappe.ui.form.on("Quotation Item", "groos_weight", function(frm) {
	set_total_weight(frm);
});


var set_cartons = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.pcs_ctn) {
		var qty = row.qty || 1;
		var cartons = Math.ceil(flt(qty) / flt(row.pcs_ctn));
		frappe.model.set_value(cdt, cdn, "cartons", cartons);
	}
}
var set_gross_weight = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.net_weight) {
		var qty = row.qty || 1;
		var gross_weight = flt(qty) * flt(row.net_weight);
		frappe.model.set_value(cdt, cdn, "gross_weight", gross_weight);
	}
}

var set_total_cartons = function(frm) {
	let sum_cartons = 0;
	$.each(frm.doc.items, function(i, d) {
		sum_cartons += d.cartons;
	});
	frm.set_value("total_cartons", sum_cartons);
	frm.set_df_property("total_cartons", "read_only", 1);
}

var set_total_weight = function(frm) {
	let total_weight = 0;
	$.each(frm.doc.items, function(i, d) {
		total_weight += d.gross_weight;
	});
	frm.set_value("total_weight_pkg", total_weight);
	frm.set_df_property("total_weight_pkg", "read_only", 1);
}

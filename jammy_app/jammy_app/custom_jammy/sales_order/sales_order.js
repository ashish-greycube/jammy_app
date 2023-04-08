// frappe.ui.form.on('Sales Order', {
// 	refresh: function (frm) {
// 		frappe.db.get_value('Terms and Conditions', {
// 			'is_default': 1
// 		}, 'name', (r) => {
// 			frm.set_value('tc_name', r.name);
// 		});
// 	},

// });
// frappe.ui.form.on("Sales Order Item", "cartons", function(frm, cdt, cdn){
// 	var items = frm.doc.items
// 	let total_cartons =0;
// 	for(var i in items) {
// 		total_cartons = total_cartons + items[i].cartons
// 	}
//    	frm.set_value('total_cartons', total_cartons);
//    	frm.set_df_property("total_cartons", "read_only", 1);
// });
// frappe.ui.form.on("Sales Order Item", "gross_weight", function(frm, cdt, cdn){
// 	var items = frm.doc.items
// 	let total_weight=0;
// 	for(var i in items) {
// 		total_weight = total_weight + items[i].gross_weight
// 	}
//    	frm.set_value('total_weight_pkg', total_weight);
//    	frm.set_df_property("total_weight_pkg", "read_only", 1);
// });



frappe.ui.form.on("Sales Order Item", "qty", function (frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
	set_gross_weight(frm, cdt, cdn);
	set_total_cartons(frm);
	set_total_weight(frm);

});
frappe.ui.form.on("Sales Order Item", "net_weight", function (frm, cdt, cdn) {
	set_gross_weight(frm, cdt, cdn);
	set_total_weight(frm);
});
frappe.ui.form.on("Sales Order Item", "pcs_ctn", function (frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
	set_total_cartons(frm);
});

frappe.ui.form.on("Sales Order Item", "cartons", function (frm) {
	set_total_cartons(frm);
});
frappe.ui.form.on("Sales Order Item", "groos_weight", function (frm) {
	set_total_weight(frm);
});
frappe.ui.form.on("Sales Order Item", "warehouse", function (frm, cdt, cdn) {
	set_warehouse(frm, cdt, cdn);
	set_warehouse(frm);
});

var warehouse = function (frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.warehouse) {
		var warehouse = row.warehouse || 1;
		frappe.model.set_warehouse(cdt, cdn, "warehouse", warehouse);
	}
}
var set_cartons = function (frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.pcs_ctn) {
		var qty = row.qty || 1;
		var cartons = Math.ceil(flt(qty) / flt(row.pcs_ctn));
		frappe.model.set_value(cdt, cdn, "cartons", cartons);
	}
}
var set_gross_weight = function (frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.net_weight) {
		var qty = row.qty || 1;
		var gross_weight = flt(qty) * flt(row.net_weight);
		frappe.model.set_value(cdt, cdn, "gross_weight", gross_weight);
	}
}

var set_total_cartons = function (frm) {
	let sum_cartons = 0;
	$.each(frm.doc.items, function (i, d) {
		sum_cartons += d.cartons;
	});
	frm.set_value("total_cartons", sum_cartons);
	frm.set_df_property("total_cartons", "read_only", 1);

}
var set_total_weight = function (frm) {
	let total_weight = 0;
	$.each(frm.doc.items, function (i, d) {
		total_weight += d.gross_weight;
	});
	frm.set_value("total_weight_pkg", total_weight);
	frm.set_df_property("total_weight_pkg", "read_only", 1);
}
frappe.ui.form.on("Sales Order", {
	setup: function (frm) {
		//  cur_frm.add_fetch('customer','credit_days_based_on','credit_days_based_on');
		// cur_frm.add_fetch('customer','credit_days','credit_days');
		// cur_frm.add_fetch('customer','credit_limit','credit_limit');
		cur_frm.add_fetch('customer', 'payment_terms', 'payment_terms');
		cur_frm.add_fetch('customer', 'freight_ppd', 'freight_ppd');
		cur_frm.add_fetch('customer', 'shipping_account', 'shipping_account');
		cur_frm.add_fetch('customer', 'email_option', 'email_option');

		// "ignore_pricing_rule : 1",

		cur_frm.add_fetch('item_code', 'net_weight', 'net_weight');
		cur_frm.add_fetch('item_code', 'pcs_ctn', 'pcs_ctn');
	},
	refresh: function (frm) {
		frappe.db.get_value('Terms and Conditions', {
			'is_default': 1
		}, 'name', (r) => {
			frm.set_value('tc_name', r.name);
		});
		if (frm.doc.table_items) {
			var last_id = frm.doc.table_items.length - 1;
			frappe.model.set_value(frm.doc.table_items[last_id].doctype, frm.doc.table_items[last_id].warehouse, "warehouse", frm.doc.warehouse);
		}
	}
});



frappe.ui.form.on("Sales Order Item", "batch_no", function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value("Batch", {
		"name": d.batch_no
	}, "purchase_rate", function (value) {
		d.purchase_rate = value.purchase_rate;
	});
});
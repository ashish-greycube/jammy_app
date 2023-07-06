cur_frm.add_fetch('warehouse','address_title','address_title');
cur_frm.add_fetch('warehouse','address_line1','address_line1');
cur_frm.add_fetch('warehouse','address_line2','address_line2');
cur_frm.add_fetch('warehouse','city','city');
cur_frm.add_fetch('warehouse','state','state');
cur_frm.add_fetch('warehouse','pincode','pincode');
// cur_frm.add_fetch('customer','credit_days_based_on','credit_days_based_on');
// cur_frm.add_fetch('customer','credit_days','credit_days');
// cur_frm.add_fetch('customer','credit_limit','credit_limit');
cur_frm.add_fetch('customer','payment_terms','payment_terms');
cur_frm.add_fetch('customer','freight_ppd','freight_ppd');
cur_frm.add_fetch('customer','shipping_account','shipping_account');
cur_frm.add_fetch('customer','email_option','email_option');
// "ignore_pricing_rule : 1",
cur_frm.add_fetch('item_code', 'net_weight', 'net_weight');
cur_frm.add_fetch('item_code', 'pcs_ctn', 'pcs_ctn');

frappe.ui.form.on("Delivery Note Item", "cartons", function(frm) {
	set_total_cartons(frm);
});

// frappe.ui.form.on("Delivery Note Item", "cartons", function(frm, cdt, cdn){
// 	var items = frm.doc.items
// 	let total_cartons =0;
// 	for(var i in items) {
// 		total_cartons = total_cartons + items[i].cartons
// 	}
//    	frm.set_value('total_cartons', total_cartons);
//    	frm.set_df_property("total_cartons", "read_only", 1);
// });

frappe.ui.form.on("Delivery Note Item", "groos_weight", function(frm) {
	set_total_weight(frm);
});

// frappe.ui.form.on("Delivery Note Item", "gross_weight", function(frm, cdt, cdn){
// 	var items = frm.doc.items
// 	let total_weight=0;
// 	for(var i in items) {
// 		total_weight = total_weight + items[i].gross_weight
// 	}
//    	frm.set_value('total_weight_pkg', total_weight);
//    	frm.set_df_property("total_weight_pkg", "read_only", 1);
// });

frappe.ui.form.on("Delivery Note Item", "qty", function(frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
	set_gross_weight(frm, cdt, cdn);
	set_total_cartons(frm);
	set_total_weight(frm);
});
frappe.ui.form.on("Delivery Note Item", "net_weight", function(frm, cdt, cdn) {
	set_gross_weight(frm, cdt, cdn);
	set_total_weight(frm);
});

frappe.ui.form.on("Delivery Note Item", "pcs_ctn", function(frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
	set_total_cartons(frm);
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
	let  total_weight = 0;
	$.each(frm.doc.items, function(i, d) {
		total_weight += d.gross_weight;
	});
	frm.set_value("total_weight_pkg", total_weight);
	frm.set_df_property("total_weight_pkg", "read_only", 1);
}

frappe.ui.form.on("Delivery Note", {
	refresh: function (frm) {
		frm.add_custom_button(
			"Bill Of Lading",
			function () {
				let dialog = new frappe.ui.Dialog({
					title: 'Choose Type of BOL',
					fields: [{
						label: 'Choose Type of BOL',
						fieldname: 'radio_button_container',
						fieldtype: 'HTML',
						options: `<fieldset><div><input type="radio" id="direct_item_info" name="type_of_bol" value="direct_item_info" checked><label for="direct_item_info">Direct DN Item info</label></div><div><input type="radio" id="one_line_bol" name="type_of_bol" value="one_line_bol"><label for="one_line_bol">One line BOL item</label></div><div><input type="radio" id="normal_bol" name="type_of_bol" value="normal_bol"><label for="normal_bol">Normal BOL(aggregate by item group)</label></div></fieldset>`
					}, ],
					size: 'small',
					primary_action_label: 'Create BOL',
					primary_action(values) {
						let type_of_bol = $('input[name="type_of_bol"]:checked').val();
						console.log(type_of_bol)
						dialog.fields_dict.radio_button_container.$wrapper.empty();
						dialog.hide();
						frappe.call({
							method: "jammy_app.jammy_app.custom_jammy.delivery_note.delivery_note.create_bol",
							args: {
								'doctype': 'Delivery Note',
								'docname': frm.doc.name,
								'type_of_bol': type_of_bol,
							},
							callback: function (r) {
								if (!r.exc) {
									frappe.msgprint('Bill of Lading created successfully.');
								}
							},
							success: function (r) {},
							url: "" || frappe.request.url,
						});
					}
				});
				dialog.show();
			}, "Create");
	}
})

// frappe.ui.form.on("Delivery Note Item", "batch_no", function(frm, cdt, cdn) {
//     var d = locals[cdt][cdn];
//         frappe.db.get_value("Batch", {"name": d.batch_no}, "purchase_rate", function(value) {
//             d.purchase_rate = value.purchase_rate;
//         });
// });


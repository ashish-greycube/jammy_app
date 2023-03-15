frappe.ui.form.on('Sales Order',{
	refresh:function(frm){
		frappe.db.get_value('Terms and Conditions', {'is_default': 1}, 'name', (r) => {
				frm.set_value('tc_name', r.name);
			});
	},
	
});
frappe.ui.form.on("Sales Order Item", "cartons", function(frm, cdt, cdn){
	var items = frm.doc.items
	let total_cartons =0;
	for(var i in items) {
		total_cartons = total_cartons + items[i].cartons
	}
   	frm.set_value('total_cartons', total_cartons);
   	frm.set_df_property("total_cartons", "read_only", 1);
});
frappe.ui.form.on("Sales Order Item", "gross_weight", function(frm, cdt, cdn){
	var items = frm.doc.items
	let total_weight=0;
	for(var i in items) {
		total_weight = total_weight + items[i].gross_weight
	}
   	frm.set_value('total_weight_pkg', total_weight);
   	frm.set_df_property("total_weight_pkg", "read_only", 1);
});


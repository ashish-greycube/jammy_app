cur_frm.add_fetch('item_code', 'weight_per_unit', 'weight_per_unit');
cur_frm.add_fetch('item_code', 'net_weight', 'net_weight');
cur_frm.add_fetch('item_code', 'pcs_ctn', 'pcs_ctn');
cur_frm.add_fetch('item_code', 'weight_per_pieces', 'weight_per_pieces');

frappe.ui.form.on("Stock Entry Detail", "qty", function(frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
    set_weight_per_pieces(frm, cdt, cdn);
	set_gross_weight(frm, cdt, cdn);
	set_total_cartons(frm);
	set_total_weight(frm);
	
});
frappe.ui.form.on("Stock Entry Detail", "net_weight", function(frm, cdt, cdn) {
	set_gross_weight(frm, cdt, cdn);
	set_total_weight(frm);
	set_weight_per_pieces(frm);
});
frappe.ui.form.on("Stock Entry Detail", "pcs_ctn", function(frm, cdt, cdn) {
	set_cartons(frm, cdt, cdn);
	set_total_cartons(frm);
});

frappe.ui.form.on("Stock Entry Detail", "cartons", function(frm) {
	set_total_cartons(frm);
});
frappe.ui.form.on("Stock Entry Detail", "gross_weight", function(frm) {
	set_total_weight(frm);
});
frappe.ui.form.on("Stock Entry Detail", "warehouse", function(frm, cdt, cdn) {
	set_warehouse(frm, cdt, cdn);
	set_warehouse(frm);
});

var warehouse = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.warehouse) {
		var warehouse = row.warehouse || 1;
		frappe.model.set_warehouse(cdt, cdn, "warehouse", warehouse);
	}
};

var set_cartons = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.pcs_ctn) {
		var qty = row.qty || 1;
		var cartons = (flt(qty) / flt(row.pcs_ctn));
		frappe.model.set_value(cdt, cdn, "cartons", cartons);
	}
};
var set_gross_weight = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.net_weight) {
		var qty = row.qty || 1;
		var gross_weight = flt(qty) * flt(row.net_weight);
		frappe.model.set_value(cdt, cdn, "gross_weight", gross_weight);
	}
};

var set_total_cartons = function(frm, cdt, cdn) {
	let sum_cartons = 0;
	$.each(frm.doc.items, function(i, d) {
		sum_cartons += d.cartons;
	});
	frm.set_value("total_cartons", sum_cartons);
};
var set_total_weight = function(frm, cdt, cdn) {
	let total_weight = 0;
	$.each(frm.doc.items, function(i, d) {
		total_weight += d.gross_weight;
	});
	frm.set_value("total_weight_pkg", total_net_weight);

};

 frappe.ui.form.on("Stock Entry", { 
	 refresh: function(frm, cdt, cdn) { 
	 if(frm.doc.table_items){
		 var last_id = frm.doc.table_items.length - 1;
		  frappe.model.set_value(frm.doc.table_items[last_id].doctype, frm.doc.table_items[last_id].warehouse, "warehouse", frm.doc.warehouse); } 
		}
	  });

frappe.ui.form.on("Stock Entry Detail", {
	pcs_ctn(frm,cdt,cdn){
		set_catron_weight(frm,cdt,cdn)
		set_total_carton_weight(frm,cdt,cdn)

	},
	weight_per_unit(frm,cdt,cdn){
		set_catron_weight(frm,cdt,cdn)
		set_total_carton_weight(frm,cdt,cdn)
	},
	items_remove(frm,cdt,cdn){
		set_total_carton_weight(frm,cdt,cdn)
	}
})

let set_catron_weight = function(frm, cdt, cdn){
	let row = locals[cdt][cdn]
	if (row.pcs_ctn && row.weight_per_unit){
		let carton_weight = row.pcs_ctn * row.weight_per_unit
		frappe.model.set_value(cdt,cdn,"custom_carton_weight",carton_weight)
	}
}

let set_total_carton_weight = function(frm,cdt,cdn){
	let stock_item = frm.doc.items
	let total_carton_weight = 0
	for( let row of stock_item){
		total_carton_weight = total_carton_weight + (row.pcs_ctn * row.weight_per_unit)
	}
	frm.set_value("custom_total_carton_weight",total_carton_weight)
}
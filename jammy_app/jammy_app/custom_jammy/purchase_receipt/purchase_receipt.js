frappe.ui.form.on("Purchase Receipt", {
    "refresh": function(frm) {
		$.each(frm.doc.items, function(index,row){
			me.frm.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Purchase Order Item",
					fieldname: "batch_no",
					parent: 'Purchase Order',
					filters: { name: row.purchase_order_item },
				},
				callback: function(r) {
					if(r.message) {
						frappe.model.set_value(row.doctype, row.name, 'batch_no', r.message.batch_no)
					}
				}
			});
		});	
			refresh_field('items')
	}
});
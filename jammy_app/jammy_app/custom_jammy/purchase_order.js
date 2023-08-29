// cur_frm.add_fetch('item_code', 'pcs_ctn', 'pcs_ctn');
frappe.ui.form.on("Purchase Order", {
	schedule_date: function(frm) {
		$.each(frm.doc.items || [], function(i, d) {
			d.schedule_date = frm.doc.schedule_date;
		});
		refresh_field("items");
	},    
    // refresh:function (frm) {
    //     console.log(2)
    // },
    validate:function (frm) {
        for (var i = 0; i < cur_frm.doc.items.length; i++) {
            cur_frm.doc.items[i].transaction_date = cur_frm.doc.transaction_date
        }
        cur_frm.refresh_field('items')

        for (var i = 0; i < cur_frm.doc.items.length; i++) {
            cur_frm.doc.items[i].purchase_order_no = cur_frm.doc.purchase_order_no
        }
        cur_frm.refresh_field('items')        
    },
    // before_save: async function (frm) {
    //     console.log('start of validate')
    //     await call_main(frm)
    //     console.log('end of validate')
    //     cur_frm.refresh_field('items')
    // }
})


frappe.ui.form.on("Purchase Order Item", {
	pcs_ctn: function(frm, cdt, cdn) {
        set_cartons(frm, cdt, cdn);

	},

	qty: function(frm, cdt, cdn) {
        set_cartons(frm, cdt, cdn);
	}
});

var set_cartons = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.pcs_ctn) {
		var qty = row.qty || 1;
		var cartons = (flt(qty) / flt(row.pcs_ctn));
		frappe.model.set_value(cdt, cdn, "cartons", cartons);
	}
}
async function call_main(frm) {
    for (var i = 0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].item_name==undefined || frm.doc.items[i].item_name=='' || frm.doc.items[i].description==undefined  || frm.doc.items[i].description==''){
            let values = await get_closed_taks(frm.doc.items[i].item_code)
            
            console.log(values,'item_name,description')
            frm.doc.items[i].item_name=values.item_name
            frm.doc.items[i].description=values.description
            console.log(frm.doc.items[i],'frm.doc.items[i]')
        }
    }
    cur_frm.refresh_field('items')

}


function get_closed_taks(item_code) {
    return new Promise((resolve, reject) => {
        frappe.db.get_value('Item', item_code, ['item_name', 'description'])
        .then(r => {
            let values = r.message;
            console.log('values',values)
            return resolve(values)
        })
    })
}
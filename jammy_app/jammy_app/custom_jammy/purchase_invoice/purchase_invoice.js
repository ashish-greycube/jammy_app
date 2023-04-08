// frappe.ui.form.on('Purchase Invoice',{
// 	refresh:function(frm){	
// 			console.log("---------------------");
// 			$.each(frm.doc.items, function(index,row){
// 				console.log("=======test========")
// 				frappe.db.get_value('Purchase Receipt Item', { name: row.purchase_receipt_item },'batch_no', function(data){
//  				row.batch_no= data.batch_no})

//  			});

// 			refresh_field('items')	
// 	},
// });
frappe.ui.form.on("Purchase Invoice", "validate", function () {
    for (var i = 0; i < cur_frm.doc.items.length; i++) {
        cur_frm.doc.items[i].transaction_date = cur_frm.doc.transaction_date
    }
    cur_frm.refresh_field('items')
});

frappe.ui.form.on("Purchase Invoice", "validate", function () {
    for (var i = 0; i < cur_frm.doc.items.length; i++) {
        cur_frm.doc.items[i].purchase_order_no = cur_frm.doc.purchase_order_no
    }
    cur_frm.refresh_field('items')
});
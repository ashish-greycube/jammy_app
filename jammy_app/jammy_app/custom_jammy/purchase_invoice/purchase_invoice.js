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

// frappe.ui.form.on('Purchase Receipt', {
//     refresh(frm) {
//         // cur_frm.add_fetch('item_code', 'net_weight', 'net_weight');
//         cur_frm.add_fetch('item_code', 'pcs_ctn', 'pcs_ctn');


//     }
// })

// below enable if required

// frappe.ui.form.on("Purchase Invoice Item", "qty", function (frm, cdt, cdn) {
//     set_cartons(frm, cdt, cdn);
//     set_gross_weight(frm, cdt, cdn);
//     set_total_cartons(frm);
//     set_total_weight(frm);
// });
// frappe.ui.form.on("Purchase Invoice Item", "net_weight", function (frm, cdt, cdn) {
//     set_gross_weight(frm, cdt, cdn);
//     set_total_weight(frm);
// });
// frappe.ui.form.on("Purchase Invoice Item", "pcs_ctn", function (frm, cdt, cdn) {
//     set_cartons(frm, cdt, cdn);
//     set_total_cartons(frm);
// });

// frappe.ui.form.on("Purchase Invoice Item", "cartons", function (frm) {
//     set_total_cartons(frm);
// });
// frappe.ui.form.on("Purchase Invoice Item", "groos_weight", function (frm) {
//     set_total_weight(frm);
// });


// var set_cartons = function (frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     if (row.pcs_ctn) {
//         var qty = row.qty || 1;
//         var cartons = Math.ceil(flt(qty) / flt(row.pcs_ctn));
//         frappe.model.set_value(cdt, cdn, "cartons", cartons);
//     }
// }
// var set_gross_weight = function (frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     if (row.net_weight) {
//         var qty = row.qty || 1;
//         var gross_weight = flt(qty) * flt(row.net_weight);
//         frappe.model.set_value(cdt, cdn, "gross_weight", gross_weight);
//     }
// }

// var set_total_cartons = function (frm) {
//     let sum_cartons = 0;
//     $.each(frm.doc.items, function (i, d) {
//         sum_cartons += d.cartons;
//     });
//     frm.set_value("total_cartons", sum_cartons);
// }
// var set_total_weight = function (frm) {
//     let total_weight = 0;
//     $.each(frm.doc.items, function (i, d) {
//         total_weight += d.gross_weight;
//     });
//     frm.set_value("total_weight_pkg", total_weight);
// }
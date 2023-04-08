frappe.ui.form.on("Purchase Order", "validate", function () {
    for (var i = 0; i < cur_frm.doc.items.length; i++) {
        cur_frm.doc.items[i].transaction_date = cur_frm.doc.transaction_date
    }
    cur_frm.refresh_field('items')
});

frappe.ui.form.on("Purchase Order", "validate", function () {
    for (var i = 0; i < cur_frm.doc.items.length; i++) {
        cur_frm.doc.items[i].purchase_order_no = cur_frm.doc.purchase_order_no
    }
    cur_frm.refresh_field('items')
});
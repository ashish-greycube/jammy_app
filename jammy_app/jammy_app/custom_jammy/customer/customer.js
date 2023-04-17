frappe.ui.form.on("Customer", {
	refresh: function(frm) {
		if(!frm.doc.__islocal) {
            frappe.route_options = {
                "company": frappe.defaults.get_default('company'),
                "ageing_based_on":"Due Date",
                "report_date":frappe.datetime.get_today(),
                "range1":"30",
                "range2":"60",
                "range3":"90",
                "range4":"120",
                "customer":frm.doc.name,
            };
			frm.add_custom_button(__('Jammy Accounts Receivable'), function () {
				frappe.set_route('query-report', 'Jammy Accounts Receivable');
			}, __('View'));
        }
    }
})
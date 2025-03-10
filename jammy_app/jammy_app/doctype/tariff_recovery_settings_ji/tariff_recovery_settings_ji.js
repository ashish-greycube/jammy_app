// Copyright (c) 2025, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tariff Recovery Settings JI', {
	refresh: function(frm) {
		frm.set_query("tariff_recovery_account", function () {
			var account_type = ["Tax", "Chargeable", "Expense Account"];
			return {
				query: "erpnext.controllers.queries.tax_account_query",
				filters: {
					"account_type": account_type,
					"company": frappe.defaults.get_default("company"),
				}
			}
		});
	}
});

// Copyright (c) 2023, frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Jammy  Print Price List"] = {
	"filters": [
		{
			"fieldname":"price_list",
			"label":("Price List"),
			"fieldtype":"Link",
			"options":"Price List",
		},

	],
	onload: (report) => {
		report.page.add_inner_button(__("Print Price List"), () => {
			let filters = report.get_values();
			let price_list = filters.price_list ;
			if(!report.data || !price_list) {
				frappe.msgprint(__('Select Price List'));
				return;
			}
			let url = `/api/method/jammy_app.jammy_app.report.jammy__print_price_list.jammy__print_price_list.get_print_pdf`;
			open_url_post(url, filters, true);				
		});

	},
};

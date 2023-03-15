// Copyright (c) 2016, frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Statement"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname":"credit_days_based_on",
			"label": __("Credit Days Based On"),
			"fieldtype": "Select",
			"options": "\nFixed Days\nLast Day of the Next Month"
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"report_date",
			"label": __("As on Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"ageing_based_on",
			"label": __("Ageing Based On"),
			"fieldtype": "Select",
			"options": 'Posting Date\nDue Date',
			"default": "Posting Date"
		},
		{
			"fieldname":"range1",
			"label": __("Ageing Range 1"),
			"fieldtype": "Int",
			"default": "30",
			"reqd": 1
		},
		{
			"fieldname":"range2",
			"label": __("Ageing Range 2"),
			"fieldtype": "Int",
			"default": "60",
			"reqd": 1
		},
		{
			"fieldname":"range3",
			"label": __("Ageing Range 3"),
			"fieldtype": "Int",
			"default": "90",
			"reqd": 1
		}

	],

	onload: function(report) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Jammy Settings",
				fieldname: ['date_time_for_customer_statement', 'report_manager']
			},
			callback: function(r) {
				if(r.message) {
					var now_datetime = new Date()
					var last_generated_datetime = new Date(r.message.date_time_for_customer_statement)
					last_generated_datetime.setMinutes(last_generated_datetime.getMinutes() + 60)
					if(now_datetime > last_generated_datetime){
						report.page.add_inner_button(__("Generate Customer Statement"), function() {
							var date_to_set = frappe.datetime.now_datetime()
							$("button:contains('Generate Customer Statement')").addClass("hide")
							frappe.call({
								method : "jammy_app.jammy_app.report.customer_statement.customer_statement.generate_customer_statement",
								args: {
									'data': frappe.query_report.data,
									'filters': report.get_values(),
									'report_manager' : r.message.report_manager
								},
								callback: function(r){

								}
							});
						});
					}
				}
			}
		});
	}
}

// Copyright (c) 2025, frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Jammy Customer Item Analytics"] = {
	"filters": [
		{
			fieldname: 'from_date',
			fieldtype: 'Date',
			label: 'From Date',
			default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
			reqd: 1
		},
		{
			fieldname: 'to_date',
			fieldtype: 'Date',
			label: 'To Date',
			default: frappe.datetime.nowdate(),
			reqd: 1
		},
		{
			fieldname: 'company',
			fieldtype: 'Link',
			label: 'Company',
			options: 'Company',
			reqd: 1
		},
		{
			fieldname: 'customer',
			fieldtype: 'Link',
			label: 'Customer',
			options: 'Customer',
			reqd: 1
		},
	]
};

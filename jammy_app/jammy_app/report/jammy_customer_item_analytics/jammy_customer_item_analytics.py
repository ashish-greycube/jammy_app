# Copyright (c) 2025, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: 
		filters = {}
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	if not data:
		frappe.msgprint("No data found!", alert=True)
	chart = get_chart(data)
	return columns, data, None, chart

def get_columns():
	columns = [
		dict(
			fieldname = 'item_code',
			fieldtype = "Link",
			label = _("Item"),
			options = "Item",
			width = 250
		),
		dict(
			fieldname = 'qty',
			fieldtype = "Float",
			label = _("Qty"),
			width = 180
		),
		dict(
			fieldname = 'value',
			fieldtype = "Currency",
			label = _("Value"),
			width = 180
		),
		dict(
			fieldname = 'average_rate',
			fieldtype = "Float",
			label = _("Average Rate (Value/Qty)"),
			width = 180
		)
	]
	return columns

def get_conditions(filters):
	condition = {}
	for key, value in filters.items():
		if filters.get(key):
			condition[key] = value
	return condition

def get_data(filters):
	conditions = get_conditions(filters)
	data = frappe.db.sql(
		f'''
			SELECT 
				tsi.customer as "customer", 
				tsii.item_code, 
				tsii.item_name,
				SUM(tsii.qty) as "qty", 
				SUM(tsii.amount) as "value",
				IFNULL(SUM(tsii.amount)/SUM(tsii.qty)) as "average_rate"
			FROM 
				`tabSales Invoice` tsi
			INNER JOIN 
				`tabSales Invoice Item` tsii
			ON 
				tsi.name = tsii.parent
			WHERE 
				tsi.customer = "{conditions.get('customer')}"
			AND tsi.company = "{conditions.get('company')}"
			AND tsi.is_return = "0"
			AND tsi.docstatus = "1"
			AND tsi.posting_date BETWEEN "{conditions.get('from_date')}" AND "{conditions.get('to_date')}"
			GROUP BY 
				tsii.item_code
		'''
		,as_dict = True
	)
	return data

def get_chart(data):
	chart = {
		"data" : {
			"labels" : [d.get("item_code") for d in data],
			"datasets" : [
				{
					"name" : "Quantity",
					"values" : [d.get("qty") for d in data],
				}
			],
		},
		"type" : "line",
		"title": "Customer - Item Analytics",
		"colors" : ["#7cb96c"]
	}

	return chart
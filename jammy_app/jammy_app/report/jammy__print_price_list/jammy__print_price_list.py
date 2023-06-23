# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.core.utils import html2text


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_entries(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("ID"),
			"fieldname": "id",
			"fieldtype": "Link",
			"options": "Item Price",
			"width": 150,
		},
		{
			"label": _("Price List"),
			"fieldname": "price_list",
			"fieldtype": "Link",
			"options": "Price List",
			"width": 170,
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 240,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Item Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 450,
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label": _("Pcs/Ctn"),
			"fieldname": "pcs_ctn",
			"fieldtype": "Int",
			"width": 90,
		},
	]
	return columns

def get_entries(filters):
	conditions = get_conditions(filters)

	entries = frappe.db.sql(
		"""
		SELECT
			ip.name as id, ip.price_list as price_list, ip.item_code as item_code, ip.item_name as item_name,
			ip.item_description as description, ip.price_list_rate as rate, i.pcs_ctn as pcs_ctn
		FROM 
			`tabItem Price` ip
		INNER JOIN
			`tabItem` i ON ip.item_code = i.item_code
		WHERE
			1=1
			{conditions}
		ORDER BY
            ip.price_list,ip.item_code

		""".format(conditions=conditions),filters,as_dict=1
	)
	for entry in entries:
		
		entry["description"] = html2text(entry["description"])
		
	return entries
	

def get_conditions(filters):
	
	conditions =""

	if filters.get("price_list"):
		conditions += " and ip.price_list = %(price_list)s"
	return conditions
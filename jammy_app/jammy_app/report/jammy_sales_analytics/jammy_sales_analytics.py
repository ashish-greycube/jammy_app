# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from erpnext.selling.report.sales_analytics.sales_analytics import execute as sales_analytics_execute


def execute(filters=None):
	"""Standard Sales Analytics report, plus the customer's complete address."""
	result = list(sales_analytics_execute(filters))
	columns, data = result[0], result[1]

	# "All" (Based On) forces tree type to Customer in the standard report
	filters = frappe._dict(filters or {})
	if filters.tree_type == "Customer" or filters.doc_type == "All":
		add_address_column(columns, data)

	return tuple(result)


def add_address_column(columns, data):
	# place it right after the Customer Name column
	columns.insert(
		2,
		{
			"label": _("Customer Address"),
			"fieldname": "customer_address",
			"fieldtype": "Data",
			"width": 400,
		}
	)

	customers = list({row.get("entity") for row in data if row.get("entity")})
	addresses = get_customer_addresses(customers)
	for row in data:
		if row.get("entity") in addresses:
			row["customer_address"] = addresses[row["entity"]]


def get_customer_addresses(customers):
	"""Return {customer: complete address}, using the Primary Address, else the best linked address."""
	if not customers:
		return {}

	rows = frappe.db.sql(
		"""
		select
			c.name as customer,
			concat_ws(', ',
				nullif(a.address_line1, ''),
				nullif(a.address_line2, ''),
				nullif(a.city, ''),
				nullif(a.county, ''),
				nullif(a.state, ''),
				nullif(a.pincode, ''),
				nullif(a.country, '')
			) as customer_address
		from `tabCustomer` c
		inner join `tabAddress` a on a.name = coalesce(
			nullif(c.customer_primary_address, ''),
			(
				select dl.parent
				from `tabDynamic Link` dl
				inner join `tabAddress` da on da.name = dl.parent
				where dl.parenttype = 'Address' and dl.link_doctype = 'Customer' and dl.link_name = c.name
					and da.disabled = 0
				order by da.is_primary_address desc, da.is_shipping_address asc, da.modified desc
				limit 1
			)
		)
		where c.name in %(customers)s
		""",
		{"customers": customers},
		as_dict=True,
	)

	return {d.customer: d.customer_address for d in rows}

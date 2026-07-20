import frappe
from frappe import _
from erpnext.accounts.report.item_wise_sales_register.item_wise_sales_register import execute as _execute


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""

	report_result = _execute(filters)

	if len(report_result[1])>1:
		columns = get_columns(report_result)
		data = get_data(report_result)
	else:
		columns = []
		data = []

	return columns, data

def execute_snapshot_report(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for snapshot report. When 'Synced
	Report' is enabled in report, framework will call this method
	every time the report is refreshed or a filter is updated. It
	accepts the same filters as normal execute. But a utility method -
	get_latest_sync, is also imported.

	"""
	from frappe.database.duckdb.database import get_latest_sync

	columns = get_columns()
	data = get_data()

	return columns, data

def get_columns(report_result) -> list[dict]:
	columns = report_result[0]

	tarrif_rate_col = {
		'label': 'Tariff Rate', 'fieldname': 'tariff_rate', 'fieldtype': 'Currency', 'options': 'currency', 'width': 100
	}
	tarrif_amount_col = {
		'label': 'Tariff Amount', 'fieldname': 'tariff_amount', 'fieldtype': 'Currency', 'options': 'currency', 'width': 100
	}

	insert_index = 0
	for col in columns:
		if col.get("fieldname") == "amount":
			insert_index = columns.index(col) + 1

	columns.insert(insert_index, tarrif_amount_col)
	columns.insert(insert_index, tarrif_rate_col)

	return columns


def get_data(report_result) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	data = report_result[1]

	for d in data:
		if d.get("invoice") and d.get("item_code"):
			row_data = frappe.db.sql("""
				SELECT
					sii.custom_tariff_rate AS tariff_rate,
					sii.custom_tariff_amount AS tariff_amount
				FROM
					`tabSales Invoice` si
				LEFT JOIN
					`tabSales Invoice Item` sii
				ON
					sii.parent = si.name
				WHERE
					si.name = "{0}"
					AND sii.item_code = "{1}"
			""".format(d.get("invoice"), d.get("item_code")), as_dict=1)

			if len(row_data)> 0:
				d["tariff_rate"] = row_data[0].get("tariff_rate")
				d["tariff_amount"] = row_data[0].get("tariff_amount")

	return data

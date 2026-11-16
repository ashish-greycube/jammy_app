"""Data helpers for the "Barcode Label 4x6" Delivery Note print format.

Barcode images themselves come from the bwip-js API (same as "Bar code Print Format"),
so no extra Python library is needed.
"""

import frappe

# Item Barcode "barcode_type" values used on the label
UPC_A = "UPC-A"
GTIN_14 = "GTIN-14"


def get_item_barcode(item_code, barcode_type):
	"""Return the first barcode of the given type from the Item master (Item > Barcodes table)."""
	if not item_code or not barcode_type:
		return ""
	barcode = frappe.get_all(
		"Item Barcode",
		filters={"parent": item_code, "parenttype": "Item", "barcode_type": barcode_type},
		pluck="barcode",
		order_by="idx asc",
		limit=1,
	)
	return (barcode[0] or "").strip() if barcode else ""


def get_customer_supplier_number(customer, company=None):
	"""Return our "Supplier Number" from the Customer master (Customer > Supplier Numbers table).

	Prefers the row for the Delivery Note's company, falls back to a row without company,
	then to the first row. Returns "" when the customer has none (the common case).
	"""
	if not customer:
		return ""
	rows = frappe.get_all(
		"Supplier Number At Customer",
		filters={"parent": customer, "parenttype": "Customer"},
		fields=["company", "supplier_number"],
		order_by="idx asc",
	)
	rows = [r for r in rows if (r.supplier_number or "").strip()]
	if not rows:
		return ""
	for match in (
		lambda r: company and r.company == company,
		lambda r: not r.company,
		lambda r: True,
	):
		for r in rows:
			if match(r):
				return r.supplier_number.strip()
	return ""


def normalize_gtin14(value):
	"""GTIN-8/12/13/14 -> 14 digits (left padded with zeros), or "" if not a valid GTIN length."""
	value = (value or "").strip().replace(" ", "")
	if not value.isdigit() or len(value) not in (8, 12, 13, 14):
		return ""
	return value.zfill(14)

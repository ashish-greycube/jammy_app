"""Helpers for the "Barcode Label 4x6" Delivery Note print format.

Barcodes are rendered server-side as inline SVG with physical (inch) dimensions so that
they print at an exact size on 4" x 6" labels, without any external image service.
"""

import frappe
from markupsafe import Markup, escape

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


def barcode_svg(value, symbology="code128", width_in=1.75, height_in=0.32, show_text=None):
	"""Return an inline <svg> barcode sized in inches, or "" if the value can't be encoded.

	symbology:
	- "code128": general purpose; width_in is the *maximum* width (bars are capped at 20 mil).
	- "upca": UPC-A, rendered exactly width_in x height_in including the human readable digits.
	- "itf14": GTIN-14 as ITF-14 with bearer box, rendered exactly width_in x height_in
	  (bearer box included); human readable digits are printed by the template below it.
	"""
	value = "" if value is None else str(value).strip()
	if not value:
		return ""
	try:
		if symbology == "upca":
			return _upca_svg(value, width_in, height_in, True if show_text is None else show_text)
		if symbology == "itf14":
			return _itf14_svg(value, width_in, height_in)
		return _code128_svg(value, width_in, height_in, bool(show_text))
	except Exception:
		# Invalid data for the symbology (e.g. letters in a UPC) - print nothing rather than fail
		return ""


def normalize_gtin14(value):
	"""GTIN-8/12/13/14 -> 14 digits (left padded with zeros), or "" if not a valid GTIN length."""
	value = (value or "").strip().replace(" ", "")
	if not value.isdigit() or len(value) not in (8, 12, 13, 14):
		return ""
	return value.zfill(14)


# ---------------------------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------------------------


def _runs(pattern):
	"""'1110011' -> [(start, length), ...] of bar (1) runs."""
	runs, start = [], None
	for i, bit in enumerate(pattern + "0"):
		if bit == "1" and start is None:
			start = i
		elif bit != "1" and start is not None:
			runs.append((start, i - start))
			start = None
	return runs


def _svg(width_in, height_in, vb_w, vb_h, body, label):
	# wkhtmltopdf (WebKit) lays out in whole CSS pixels (1px = 1/96in) and truncates fractions,
	# so round to the nearest pixel: e.g. 3.01in -> 289px (3.0104in) instead of 288px (3.000in).
	w_px = max(1, round(width_in * 96))
	h_px = max(1, round(height_in * 96))
	return Markup(
		f'<svg xmlns="http://www.w3.org/2000/svg" class="jl-barcode" role="img" aria-label="{escape(label)}" '
		f'width="{w_px}px" height="{h_px}px" viewBox="0 0 {vb_w:g} {vb_h:g}" '
		f'preserveAspectRatio="none" shape-rendering="crispEdges" '
		f'style="display:block;width:{w_px}px;height:{h_px}px;">{body}</svg>'
	)


def _rects(pattern, x0, y, h, unit=1, tall=None, tall_h=None):
	out = []
	for start, length in _runs(pattern):
		hh = tall_h if tall and any(start <= t < start + length for t in tall) else h
		out.append(f'<rect x="{x0 + start * unit:g}" y="{y:g}" width="{length * unit:g}" height="{hh:g}"/>')
	return "".join(out)


def _code128_svg(value, max_width_in, height_in, show_text):
	from barcode.codex import Code128

	pattern = Code128(value).build()[0]
	modules = len(pattern)
	# cap the module (narrowest bar) at 0.02" so very short values don't print huge bars
	width_in = round(min(max_width_in, modules * 0.02), 4)
	text_h = modules * 0.18 if show_text else 0  # in module units
	vb_h = modules * height_in / width_in  # keep units square
	bar_h = vb_h - text_h
	body = f'<g fill="#000">{_rects(pattern, 0, 0, bar_h)}</g>'
	if show_text:
		body += (
			f'<text x="{modules / 2:g}" y="{vb_h - text_h * 0.15:g}" text-anchor="middle" '
			f'font-family="Arial, Helvetica, sans-serif" font-size="{text_h * 0.85:g}">{escape(value)}</text>'
		)
	return _svg(width_in, height_in, modules, vb_h, body, value)


def _upca_svg(value, width_in, height_in, show_text):
	from barcode.upc import UPCA

	digits = value.replace(" ", "").replace("-", "")
	upc = UPCA(digits[:11])  # library computes the check digit
	full = upc.get_fullcode()
	if len(digits) == 12 and digits != full:
		raise ValueError("UPC-A check digit mismatch")
	pattern = upc.build()[0]  # 95 modules

	# Layout (module units, square): [7 margin + first digit][95 bars][7 last digit]
	side = 9 if show_text else 0
	vb_w = 95 + 2 * side
	vb_h = vb_w * height_in / width_in
	text_size = 9 if show_text else 0
	bar_h = vb_h - text_size - 1 if show_text else vb_h
	guard_h = vb_h - text_size * 0.45 if show_text else vb_h
	# guard bars (start, middle, end) extend down into the text area
	guards = {0, 2, 46, 48, 92, 94}
	body = f'<g fill="#000">{_rects(pattern, side, 0, bar_h, tall=guards, tall_h=guard_h)}</g>'
	if show_text:
		font = 'font-family="Arial, Helvetica, sans-serif" text-anchor="middle"'
		ty = vb_h - 0.6
		body += (
			f'<g {font} font-size="{text_size:g}">'
			f'<text x="{side * 0.25:g}" y="{ty - 1.5:g}" font-size="{text_size * 0.8:g}">{full[0]}</text>'
			f'<text x="{side + 3 + 21:g}" y="{ty:g}" textLength="40" lengthAdjust="spacingAndGlyphs">{full[1:6]}</text>'
			f'<text x="{side + 50 + 21:g}" y="{ty:g}" textLength="40" lengthAdjust="spacingAndGlyphs">{full[6:11]}</text>'
			f'<text x="{side + 95 + side * 0.75:g}" y="{ty - 1.5:g}" font-size="{text_size * 0.8:g}">{full[11]}</text>'
			f"</g>"
		)
	return _svg(width_in, height_in, vb_w, vb_h, body, f"UPC-A {full}")


def _itf14_svg(value, width_in, height_in):
	from barcode.itf import ITF

	gtin = normalize_gtin14(value)
	if not gtin:
		raise ValueError("Invalid GTIN-14")
	# narrow = 2 units, wide = 5 units (2.5:1) -> 241 units of symbol
	pattern = ITF(gtin, narrow=2, wide=5).build()[0]
	quiet = 20  # 10 x narrow bar
	bearer = 10  # 5 x narrow bar (ITF-14 spec: >= 2 x narrow)
	vb_w = len(pattern) + 2 * quiet + 2 * bearer
	vb_h = vb_w * height_in / width_in
	inner_h = vb_h - 2 * bearer
	body = (
		'<g fill="#000">'
		# bearer box
		f'<rect x="0" y="0" width="{vb_w:g}" height="{bearer:g}"/>'
		f'<rect x="0" y="{vb_h - bearer:g}" width="{vb_w:g}" height="{bearer:g}"/>'
		f'<rect x="0" y="0" width="{bearer:g}" height="{vb_h:g}"/>'
		f'<rect x="{vb_w - bearer:g}" y="0" width="{bearer:g}" height="{vb_h:g}"/>'
		f"{_rects(pattern, bearer + quiet, bearer, inner_h)}"
		"</g>"
	)
	return _svg(width_in, height_in, vb_w, vb_h, body, f"GTIN-14 {gtin}")

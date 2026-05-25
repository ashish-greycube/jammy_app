from frappe.model.document import Document
import frappe
from jammy_app.jammy_app.custom_jammy.quotation.quotation import set_total_cartons_and_total_weight

def validate(doc, method):
	set_total_cartons_and_total_weight(doc)
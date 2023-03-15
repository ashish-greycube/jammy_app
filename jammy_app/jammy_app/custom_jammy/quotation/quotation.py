from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from six import string_types

def validate(doc, method):
	set_total_cartons_and_total_weight(doc)

def set_total_cartons_and_total_weight(doc):
	total_cartons, total_weight = 0, 0 
	for item in doc.items:
		if item.cartons:
			total_cartons += item.cartons
			total_weight += item.gross_weight
	doc.total_cartons = total_cartons
	doc.total_weight_pkg = total_weight
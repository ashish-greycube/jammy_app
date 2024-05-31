from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from six import string_types

def validate(self,method):
    set_total_catron_weight_and_carton_weight(self)

def set_total_catron_weight_and_carton_weight(self):
    total_carton_weight = 0
    for row in self.get("items"):
        if row.pcs_ctn and row.weight_per_unit :
            carton_weight = row.pcs_ctn * row.weight_per_unit
            row.custom_carton_weight = carton_weight
            total_carton_weight = total_carton_weight + row.custom_carton_weight
    self.custom_total_carton_weight = total_carton_weight
    

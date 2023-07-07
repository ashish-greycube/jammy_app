# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BillOfLadingJI(Document):
    def validate(self):
        total_weight = 0
        total_cartons = 0
        pallet_for_total_carton = frappe.db.get_single_value('Bill Of Lading Settings JI', 'pallet_for_total_cartons')
        weight_of_one_pallet = frappe.db.get_single_value('Bill Of Lading Settings JI', 'weight_of_one_pallet')


        for row in self.bill_of_lading_details:
            total_weight += row.weight
            total_cartons += row.packing_units

       
        self.total_cartons = total_cartons
        if pallet_for_total_carton and pallet_for_total_carton!=0:
            self.pallet_quantity = total_cartons % pallet_for_total_carton
        else:
            self.pallet_quantity = 0
        self.total_weight = total_weight+(35 * self.pallet_quantity)
       
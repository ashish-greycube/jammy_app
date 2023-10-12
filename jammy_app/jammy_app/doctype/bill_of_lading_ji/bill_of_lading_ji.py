# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display

class BillOfLadingJI(Document):
    def validate(self):
        if not self.ship_from_address:
            ship_from_address_name=frappe.db.get_all('Dynamic Link', filters={'link_doctype': ['=', 'Warehouse'],'parenttype': ['=', 'Address'],'link_name': ['=', self.get('ship_from') ]},fields=['parent'])
            if len(ship_from_address_name)>0:
                ship_from_address_name=ship_from_address_name[0].parent
                ship_from_address_title=frappe.db.get_value('Address',ship_from_address_name, 'address_title')
                if ship_from_address_title:
                    self.ship_from_address=ship_from_address_title+'<br>'+get_address_display(ship_from_address_name)
            else:
                self.ship_from_address=get_address_display(self.get('ship_from'))

        if not self.ship_to:
            ship_to_title = frappe.db.get_value('Address', self.get('shipping_address_name'), 'address_title')
            if ship_to_title:
                self.ship_to=ship_to_title+'<br>'+get_address_display(self.get('shipping_address_name'))
            else:
                self.ship_to=get_address_display(self.get('shipping_address_name'))
        total_weight = 0
        total_cartons = 0
        pallet_for_total_carton = frappe.db.get_single_value('Bill Of Lading Settings JI', 'pallet_for_total_cartons')
        weight_of_one_pallet = frappe.db.get_single_value('Bill Of Lading Settings JI', 'weight_of_one_pallet')


        for row in self.bill_of_lading_details:
            total_weight += row.weight
            total_cartons += row.packing_units

       
        self.total_cartons = total_cartons
        if pallet_for_total_carton and pallet_for_total_carton!=0:
            self.pallet_quantity = (total_cartons // pallet_for_total_carton) + ( 1 if ((total_cartons % pallet_for_total_carton) > 0) else 0)
        else:
            self.pallet_quantity = 0
        self.total_weight = total_weight+(35 * self.pallet_quantity)
       
# Copyright (c) 2023, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display

class BillOfLadingJI(Document):
    def before_insert(self):
        self.calculate_total_weight_cartoons_and_pallet_quantity()

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

        # self.calculate_total_weight_cartoons_and_pallet_quantity()

        self.calculate_density_and_freight_class()

    def calculate_total_weight_cartoons_and_pallet_quantity(self):
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

    def calculate_density_and_freight_class(self):
        if self.pallet_length > 0 and self.pallet_width > 0 and self.pallet_height != None and self.pallet_height > 0:
            divisor = frappe.db.get_single_value("Bill Of Lading Settings JI", "density_divisor")
            if divisor != None and divisor > 0 and (self.pallet_length * self.pallet_width * self.pallet_height) > 0:
                density = (self.total_weight) / ((self.pallet_length * self.pallet_width * self.pallet_height) / divisor)
                self.density = density

                settings = frappe.get_doc("Bill Of Lading Settings JI")
                density_class = 0
                if settings:
                    for dc in settings.density_class_details:
                        if density >= dc.get("from") and density < dc.get("to"):
                            density_class = dc.get("density_class")
                            break
                    self.estimated_freight_class = density_class
                    if self.printed_freight_class == 0 or self.printed_freight_class == None:
                        self.printed_freight_class = density_class

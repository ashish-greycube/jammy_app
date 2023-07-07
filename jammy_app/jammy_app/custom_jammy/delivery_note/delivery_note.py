from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import utils
from frappe.utils.data import getdate, nowdate
from frappe.utils import get_link_to_form,flt
from six import string_types
from jammy_app.jammy_app.custom_jammy.quotation.quotation import set_total_cartons_and_total_weight
from itertools import groupby

def validate(doc, method):
	set_total_cartons_and_total_weight(doc)

@frappe.whitelist()
def create_bol(doctype,docname,type_of_bol):

	delivery_note = frappe.get_doc(doctype, docname)
	# Check if BOL already exists for the delivery note
	existing_bol = frappe.get_all('Bill Of Lading JI', filters={'ref': delivery_note.name}, limit=1)
	if existing_bol:
		frappe.throw('A Bill of Lading already exists for this Delivery Note.')

	bill_of_lading = frappe.new_doc('Bill Of Lading JI')
	
	bill_of_lading.ship_from = delivery_note.set_warehouse
	bill_of_lading.date = getdate(nowdate())
	bill_of_lading.ref = delivery_note.name
	bill_of_lading.carrier_name = delivery_note.ship_via
	bill_of_lading.shipping_address_name=delivery_note.shipping_address_name
	bill_of_lading.ship_to = delivery_note.shipping_address
	bill_of_lading.cid = delivery_note.po_no
	bill_of_lading.freight_charge_terms='Prepaid'
	bill_of_lading.third_party_freight_charges_bill_to=delivery_note.company_address_display
	total_weight = 0
	total_cartons = 0
	pallet_for_total_carton = frappe.db.get_single_value('Bill Of Lading Settings JI', 'pallet_for_total_cartons')
	weight_of_one_pallet = frappe.db.get_single_value('Bill Of Lading Settings JI', 'weight_of_one_pallet')

	
	if(type_of_bol=="direct_item_info"):
		bill_of_lading.type_of_bol='Direct DN Item info'
		for item in delivery_note.items:
			item_group = item.item_group
			nmfc_cf = frappe.get_value('Item Group', item_group, 'nmfc_cf')
			freight_class_cf = frappe.get_value('Item Group', item_group, 'freight_class_cf')
			description = f"{item.item_name}:{item.item_group}"
			weight = item.gross_weight
			total_weight += weight
			carton = item.cartons
			total_cartons += carton
			
			row = bill_of_lading.append('bill_of_lading_details',{
				"description":description,
				"weight": item.gross_weight,
				"packing_units": item.cartons,
				"nmfc": nmfc_cf,
				"freight_class":freight_class_cf,
			})
	
	elif(type_of_bol=="one_line_bol"):
		bill_of_lading.type_of_bol='One line BOL item'
		
		aggregated_weight = sum([float(item.gross_weight) for item in delivery_note.items])
		aggregated_cartons = sum([float(item.cartons) for item in delivery_note.items])
		total_weight=aggregated_weight
		total_cartons=aggregated_cartons
		one_line_bol_item_description = frappe.db.get_single_value('Bill Of Lading Settings JI', 'one_line_bol_item_description')
		one_line_bol_item_nmfc = frappe.db.get_single_value('Bill Of Lading Settings JI', 'one_line_bol_item_nmfc')
		one_line_bol_item_freight_class = frappe.db.get_single_value('Bill Of Lading Settings JI', 'one_line_bol_item_freight_class')

		row = bill_of_lading.append('bill_of_lading_details',{
				"description":one_line_bol_item_description,
				"weight": aggregated_weight,
				"packing_units": aggregated_cartons,
				"nmfc": one_line_bol_item_nmfc,
				"freight_class":one_line_bol_item_freight_class,
			})

	elif(type_of_bol=="normal_bol"):
		bill_of_lading.type_of_bol='Normal BOL(aggregate by item group)'
		bol_rows=[]
		for item in delivery_note.items:
			if not any(d['description'] == item.item_group for  d in bol_rows):
				nmfc_cf = frappe.get_value('Item Group', item.item_group, 'nmfc_cf')
				freight_class_cf = frappe.get_value('Item Group',item.item_group, 'freight_class_cf')	
				total_weight=total_weight+item.gross_weight		
				total_cartons=total_cartons+item.cartons
				bol_rows.append({'description':item.item_group,'weight':item.gross_weight,'packing_units':item.cartons,'nmfc':nmfc_cf,'freight_class':freight_class_cf})
			else:
				for d in bol_rows:
					if d['description'] ==item.item_group:
						d['weight']=d['weight']+item.gross_weight
						d['packing_units']=d['packing_units']+item.cartons
						total_weight=total_weight+item.gross_weight		
						total_cartons=total_cartons+item.cartons						
						break
		for row in bol_rows:
			bill_of_lading.append('bill_of_lading_details',row)

	bill_of_lading.total_cartons = total_cartons
	bill_of_lading.pallet_quantity = total_cartons % pallet_for_total_carton
	bill_of_lading.total_weight = total_weight+(35 * bill_of_lading.pallet_quantity)
	bill_of_lading.save(ignore_permissions=True)
	msg = ('Bill Of Lading {} is created'.format(frappe.bold(get_link_to_form('Bill Of Lading JI', bill_of_lading.name))))
	frappe.msgprint(msg)

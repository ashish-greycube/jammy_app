from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from six import string_types
from jammy_app.jammy_app.custom_jammy.quotation.quotation import set_total_cartons_and_total_weight

def validate(doc, method):
	set_total_cartons_and_total_weight(doc)

def set_batch_tariff_recovery(doc, method):
	for row in doc.items:
		if row.batch_no:
			batch_tariff_recovery = frappe.db.get_value('Batch', row.batch_no, 'custom_tariff_recovery')
			row.custom_tariff_recovery = batch_tariff_recovery if batch_tariff_recovery else 0

def set_tariff_if_applicable(doc, method):
	print("mein function mein hoon")
	total_dt_tariff_amount = 0
	tariff_recovery_account = frappe.db.get_single_value('Tariff Recovery Settings JI', 'tariff_recovery_account')
	if tariff_recovery_account == None or tariff_recovery_account == '':
		frappe.throw("Tariff Recovery Account not set in Tariff Recovery Settings")

	if doc.custom_apply_tariff == 1:
		for row in doc.items:
			if row.custom_tariff_recovery and row.custom_tariff_recovery > 0:
				row.custom_tariff_rate = (row.rate * row.custom_tariff_recovery) / 100
				row.custom_tariff_amount = (row.amount * row.custom_tariff_recovery) / 100

				total_dt_tariff_amount = total_dt_tariff_amount + row.custom_tariff_amount

		doc.custom_dt_tariff_amount = total_dt_tariff_amount

		if doc.custom_dt_tariff_amount > 0:
				tariff_recovery_account_found = False
				for tax in doc.taxes:
					if tax.charge_type == 'Actual' and tax.account_head == tariff_recovery_account:
						tax.tax_amount = doc.custom_dt_tariff_amount
						tariff_recovery_account_found = True
						break

				if tariff_recovery_account_found == False:
					doc.append('taxes', {
						'charge_type': 'Actual',
						'account_head': tariff_recovery_account,
						'tax_amount': doc.custom_dt_tariff_amount,
						'description': tariff_recovery_account
					})
	
	else:
		for row in doc.items:
			row.custom_tariff_rate = 0
			row.custom_tariff_amount = 0
		
		doc.custom_dt_tariff_amount = 0

		for tax in doc.taxes:
			if tax.charge_type == 'Actual' and tax.account_head == tariff_recovery_account:
				doc.remove(tax)
				break
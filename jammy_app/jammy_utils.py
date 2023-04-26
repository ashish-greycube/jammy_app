from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt, cint
import json
import unicodedata
import re
from datetime import datetime, date
# final good
@frappe.whitelist()
def customer_statement(data, filters):
	data = json.loads(data)
	filters = json.loads(filters)
	map(lambda d: [d.pop(k) for k in ['credit_note', 'remarks', \
		'territory', 'customer_group']], data)
	
	pe_references = []
	si_references = []

	for row in data:
		if row.get('posting_date'):
			row['posting_date'] = row.get('posting_date')
		if row.get('due_date'):
			row['due_date'] = row.get('due_date')
		if row.get('voucher_type')=="Payment Entry":
			pe_references.append(row.get("voucher_no"))
		if row.get('voucher_type')=="Sales Invoice":
			si_references.append(row.get("voucher_no"))
		
	# Fetch PE reference_no in 'Your Reference' column
	if pe_references:		
		pe_references_ = [unicodedata.normalize('NFKD', i)for i in pe_references]
		if len(pe_references_) == 1 :
			{i.get('name'): i.get('reference_no') for i in frappe.db.sql("""select name,reference_no from \
			`tabPayment Entry` where name = '{0}' and reference_no is not null""".format(pe_references_[0]), as_dict=1)}
		else :
			pe_references_ = {i.get('name'): i.get('reference_no') for i in frappe.db.sql("""select name,reference_no from \
			`tabPayment Entry` where name in {0} and reference_no is not null""".format(tuple(pe_references_)), as_dict=1)}
	# Fetch SE po_no in 'Your Reference' column
	if si_references:
		si_references_ = [unicodedata.normalize('NFKD', i) for i in si_references]
		if len(si_references_) == 1 :
			si_references_ = {i.get('name'): i.get('po_no') for i in frappe.db.sql("""select name,po_no from \
			`tabSales Invoice` where name ='{0}' and po_no is not null""".format(si_references_[0]), as_dict=1)}
		else:
			si_references_ = {i.get('name'): i.get('po_no') for i in frappe.db.sql("""select name,po_no from \
			`tabSales Invoice` where name in {0} and po_no is not null""".format(tuple(si_references_)), as_dict=1)}
	# Fetch address
	address_details = {i.get('link_name'):i for i in frappe.db.sql("""
		select 
			dl.link_name, cs.address_line1, cs.address_line2, cs.city, cs.state, 
			cs.country, cs.pincode 
		from 
			`tabAddress` as cs 
		inner join 
			`tabDynamic Link` as dl on dl.parent = cs.name 
		where 
			dl.link_doctype = 'Customer' and cs.address_type = 'billing' 
		order by cs.creation asc;""",as_dict=1)}

	pe_date_list = []
	for row in data:
		if row.get('voucher_type') == "Sales Invoice":
			if si_references_:
				row.update({"your_reference": si_references_.get(row.get('voucher_no'))})
		elif row.get('voucher_type') == "Payment Entry":
			dt_format = frappe.db.get_value("System Settings", "System Settings", "date_format")
			payment_entry_date= frappe.db.get_value("Payment Entry", {'name':row.get('voucher_no') },'posting_date')
			pe_date_list.append(payment_entry_date) if payment_entry_date else 0 
			if len(pe_references_) == 1 :
				row.update({"your_reference": pe_references_})
			else:
				row.update({"your_reference": pe_references_.get(row.get('voucher_no'))})
		if pe_date_list:
			row.update({"payment_entry_date": pe_date_list[-1]})
		row.update({"address": address_details.get(row.get('party'))})
	data = sorted(data, key=lambda k: k['party'])
	
	party_current_due_amount=0.0
	for dc in data:
		if dc['age'] and flt(dc['age'])<0 and dc.get('party')!='':
			party_current_due_amount=float(flt(dc['outstanding'])+flt(party_current_due_amount))

	final_report_dict = {}
	for d in data:
		if d.get('party') in final_report_dict:
			if d['outstanding']:
				d['outstanding'] = "{:,.2f}".format(d['outstanding'])
			if not d['posting_date'] == '':
				d['posting_date'] = change_date_format(d['posting_date'])
			if 'due_date' in d:
				if not d['due_date'] == '':
					d['due_date'] = change_date_format(d['due_date'])
			if not d['range1'] == '':
				d['range1'] = format(float(d['range1']),".2f")
			if not d['range2'] == '':
				d['range2'] = format(float(d['range2']),".2f")
			if not d['range3'] == '':
				d['range3'] = format(float(d['range3']),".2f")
			if not d['range4'] == '':
				d['range4'] = format(float(d['range4']),".2f")
			if not d['range5'] == '':
				d['range5'] = format(float(d['range5']),".2f")
			final_report_dict[d.get('party')].append(d)
		else:
			if d['outstanding']:
				d['outstanding'] = "{:,.2f}".format(d['outstanding'])
			if not d['posting_date'] == '':
				print(d['posting_date'])
				d['posting_date'] = change_date_format(d['posting_date'])
				print(d['posting_date'])
			if 'due_date' in d:
				if not d['due_date'] == '':
					d['due_date'] = change_date_format(d['due_date'])
			if not d['range1'] == '':
				d['range1'] = format(float(d['range1']),".2f")
			if not d['range2'] == '':
				d['range2'] = format(float(d['range2']),".2f")
			if not d['range3'] == '':
				d['range3'] = format(float(d['range3']),".2f")
			if not d['range4'] == '':
				d['range4'] = format(float(d['range4']),".2f")
			if not d['range5'] == '':
				d['range5'] = format(float(d['range5']),".2f")
			final_report_dict.update({d.get('party'): [d]})
		d['party_current_due_amount']=format(float(party_current_due_amount),".2f")
	final_report_dict1 = list(final_report_dict)
	return final_report_dict

def change_date_format(dt):
	oldformat = dt.replace("-","")
	datetimeobject = datetime.strptime(oldformat,'%Y%m%d')
	newformat = datetimeobject.strftime('%m-%d-%Y')
	return newformat

# def change_date_format(dt):
#         return re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', dt)

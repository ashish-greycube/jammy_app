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
	print(data)
	filters = json.loads(filters)
	map(lambda d: [d.pop(k, None) for k in ['credit_note', 'remarks', \
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
			dt_format = frappe.db.get_single_value("System Settings","date_format")
			payment_entry_date= frappe.db.get_value("Payment Entry", {'name':row.get('voucher_no') },'posting_date')
			pe_date_list.append(payment_entry_date) if payment_entry_date else 0 
			if len(pe_references_) == 1 :
				row.update({"your_reference": pe_references_})
			else:
				row.update({"your_reference": pe_references_.get(row.get('voucher_no'))})
		if pe_date_list:
			row.update({"payment_entry_date": pe_date_list[-1]})
		row.update({"address": address_details.get(row.get('party'))})
	data = sorted(data, key=lambda k: k['party'] if 'party' in k else 'customer')
	
	age_field_name = ""
	outstanding_amount_field_name = ""

	party_current_due_amount=0.0
	for dc in data:

		if "age_(days)" in dc:
			age_field_name = "age_(days)"
		elif "age" in dc:
			age_field_name = "age"

		if "outstanding_amount" in dc:
			outstanding_amount_field_name = "outstanding_amount"
		elif "outstanding" in dc:
			outstanding_amount_field_name = "outstanding"

		if dc[age_field_name] and flt(dc[age_field_name])<0 and dc.get('customer')!='':
			party_current_due_amount=float(flt(dc[outstanding_amount_field_name])+flt(party_current_due_amount))

	final_report_dict = {}
	for d in data:
		if d.get('party') in final_report_dict:
			if d[outstanding_amount_field_name]:
				d[outstanding_amount_field_name] = "{:,.2f}".format(d[outstanding_amount_field_name])
			if not d['posting_date'] == '':
				d['posting_date'] = change_date_format(d['posting_date'])
			if 'due_date' in d:
				if not d['due_date'] == '':
					d['due_date'] = change_date_format(d['due_date'])

			if 'range1' in filters and f"0_{filters['range1']}" in d and d[f"0_{filters['range1']}"] != '':
				d[f"0_{filters['range1']}"] = format(float(d[f"0_{filters['range1']}"]), ".2f")

			if (
				'range1' in filters and 'range2' in filters and
				f"{filters['range1']+1}_{filters['range2']}" in d and
				d[f"{filters['range1']+1}_{filters['range2']}"] != ''
			):
				d[f"{filters['range1']+1}_{filters['range2']}"] = format(
					float(d[f"{filters['range1']+1}_{filters['range2']}"]), ".2f"
				)

			if (
				'range2' in filters and 'range3' in filters and
				f"{filters['range2']+1}_{filters['range3']}" in d and
				d[f"{filters['range2']+1}_{filters['range3']}"] != ''
			):
				d[f"{filters['range2']+1}_{filters['range3']}"] = format(
					float(d[f"{filters['range2']+1}_{filters['range3']}"]), ".2f"
				)

			if (
				'range3' in filters and 'range4' in filters and
				f"{filters['range3']+1}_{filters['range4']}" in d and
				d[f"{filters['range3']+1}_{filters['range4']}"] != ''
			):
				d[f"{filters['range3']+1}_{filters['range4']}"] = format(
					float(d[f"{filters['range3']+1}_{filters['range4']}"]), ".2f"
				)

			if 'range5' in filters and f"{filters['range5']}_above" in d and d[f"{filters['range5']}_above"] != '':
				d[f"{filters['range5']}_above"] = format(
					float(d[f"{filters['range5']}_above"]), ".2f"
				)
			final_report_dict[d.get('party')].append(d)
		else:
			if d[outstanding_amount_field_name]:
				d[outstanding_amount_field_name] = "{:,.2f}".format(d[outstanding_amount_field_name])
			if not d['posting_date'] == '':
				print(d['posting_date'])
				d['posting_date'] = change_date_format(d['posting_date'])
				print(d['posting_date'])
			if 'due_date' in d:
				if not d['due_date'] == '':
					d['due_date'] = change_date_format(d['due_date'])
			if 'range1' in filters and f"0_{filters['range1']}" in d and d[f"0_{filters['range1']}"] != '':
				d[f"0_{filters['range1']}"] = format(float(d[f"0_{filters['range1']}"]), ".2f")

			if (
				'range1' in filters and 'range2' in filters and
				f"{filters['range1']+1}_{filters['range2']}" in d and
				d[f"{filters['range1']+1}_{filters['range2']}"] != ''
			):
				d[f"{filters['range1']+1}_{filters['range2']}"] = format(
					float(d[f"{filters['range1']+1}_{filters['range2']}"]), ".2f"
				)

			if (
				'range2' in filters and 'range3' in filters and
				f"{filters['range2']+1}_{filters['range3']}" in d and
				d[f"{filters['range2']+1}_{filters['range3']}"] != ''
			):
				d[f"{filters['range2']+1}_{filters['range3']}"] = format(
					float(d[f"{filters['range2']+1}_{filters['range3']}"]), ".2f"
				)

			if (
				'range3' in filters and 'range4' in filters and
				f"{filters['range3']+1}_{filters['range4']}" in d and
				d[f"{filters['range3']+1}_{filters['range4']}"] != ''
			):
				d[f"{filters['range3']+1}_{filters['range4']}"] = format(
					float(d[f"{filters['range3']+1}_{filters['range4']}"]), ".2f"
				)

			if 'range5' in filters and f"{filters['range5']}_above" in d and d[f"{filters['range5']}_above"] != '':
				d[f"{filters['range5']}_above"] = format(
					float(d[f"{filters['range5']}_above"]), ".2f"
				)
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

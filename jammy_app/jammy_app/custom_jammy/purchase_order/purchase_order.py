from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from six import string_types
from jammy_app.jammy_app.custom_jammy.quotation.quotation import set_total_cartons_and_total_weight
from frappe.model.naming import make_autoname

def validate(doc, method):
    if doc.auto_create_supplier_based_batch_no_cf and doc.auto_create_supplier_based_batch_no_cf==1:
        supplier_batch_number_series_cf = frappe.db.get_value('Supplier', doc.supplier, 'supplier_batch_number_series_cf')
        if supplier_batch_number_series_cf:
            for item in doc.get("items"):
                if item.batch_no==None or item.batch_no=='':
                    is_stock_item = frappe.db.get_value('Item', item.item_code, 'is_stock_item')
                    if is_stock_item==1:
                        batch_id = make_autoname(supplier_batch_number_series_cf, "Batch")
                        new_batch = frappe.new_doc('Batch')
                        new_batch.batch_id =batch_id
                        new_batch.item=item.item_code
                        new_batch.save()                    
                        item.batch_no=batch_id
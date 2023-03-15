# -*- coding: utf-8 -*-
# Copyright (c) 2020, frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime

class JammySettings(Document):
	pass

@frappe.whitelist()
def get_time(set_date):
	print("--------------------------",set_date)
	doc.date_time = set_date
	
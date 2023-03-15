# -*- coding: utf-8 -*-
# Copyright (c) 2020, frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from frappe.utils import get_url, flt, nowdate
import os
import shutil
from datetime import datetime


class CustomerStatement(Document):
	pass


# @frappe.whitelist()
# def get_html_file(doc):
# 	doc = json.loads(doc)
# 	f = open('./jammy3/public/files/customer_statement_report.html', 'r')
	# print("/////////f.read()", f.read())
	
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "jammy_app"
app_title = "Jammy_app"
app_publisher = "frappe"
app_description = "Jammy"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------
# fixtures = ['Custom Field','Property Setter','Workflow','Workflow State','Workflow Action','Role','Report','Page', 'Print Format', 'Custom Script']
# fixtures = ['Custom Field','Property Setter','Workflow','Workflow State','Workflow Action','Role','Report','Page', 'Print Format', 'Client Script']
# fixtures = ['Client Script']
# include js, css files in header of desk.html
# app_include_css = "/assets/jammy_app/css/jammy_app.css"

app_include_js = ["jammy_app.bundle.js"]

# include js, css files in header of web template
# web_include_css = "/assets/jammy_app/css/jammy_app.css"
# web_include_js = "/assets/jammy_app/js/jammy_app.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)frappe.db.get_value('Purchase Receipt Item', { name: row.purchase_receipt_item },'batch_no', function(data){
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "jammy_app.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "jammy_app.install.before_install"
after_migrate = "jammy_app.migrate.after_migrate"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "jammy_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    # 	"*": {
    # 		"on_update": "method",
    # 		"on_cancel": "method",
    # 		"on_trash": "method"
    # 	}
    "Quotation": {
        "validate": "jammy_app.jammy_app.custom_jammy.quotation.quotation.validate"
    },
    "Sales Order": {
        "validate": "jammy_app.jammy_app.custom_jammy.sales_order.sales_order.validate"
    },
    "Sales Invoice": {
        "validate": "jammy_app.jammy_app.custom_jammy.sales_invoice.sales_invoice.validate"
    },
    "Delivery Note": {
        "validate": "jammy_app.jammy_app.custom_jammy.delivery_note.delivery_note.validate"
    },
    "Packing Slip": {
        "validate": "jammy_app.jammy_app.custom_jammy.packing_slip.packing_slip.validate"
    },
}

doctype_js = {
    "Customer": "jammy_app/custom_jammy/customer/customer.js",
    "Packing Slip": "jammy_app/custom_jammy/packing_slip/packing_slip.js",
    "Quotation": "jammy_app/custom_jammy/quotation/quotation.js",
    "Purchase Invoice": "jammy_app/custom_jammy/purchase_invoice/purchase_invoice.js",
    "Purchase Receipt": "jammy_app/custom_jammy/purchase_receipt/purchase_receipt.js",
    "Sales Order": "jammy_app/custom_jammy/sales_order/sales_order.js",
    "Sales Invoice": "jammy_app/custom_jammy/sales_invoice/sales_invoice.js",
    "Terms and Conditions": "jammy_app/custom_jammy/terms_and_conditions/terms_and_conditions.js",
    "Delivery Note": "jammy_app/custom_jammy/delivery_note/delivery_note.js",
    # "Journal Entry": "jammy_app/custom_jammy/journal_entry.js",
    "Pricing Rule": "jammy_app/custom_jammy/pricing_rule.js",
    "Payment Entry": "jammy_app/custom_jammy/payment_entry.js",
    "Stock Entry": "jammy_app/custom_jammy/stock_entry.js",
    "Purchase Order": "jammy_app/custom_jammy/purchase_order.js",
}
# Scheduled Tasks
# ---------------

scheduler_events = {
    # 	"all": [
    # 		"jammy_app.tasks.all"
    # 	],
    "daily": [
        "jammy_app.jammy_app.doctype.shipping_easy_order.shipping_easy_order.notify_errors"
    ],
    # 	"hourly": [
    # 		"jammy_app.tasks.hourly"
    # 	],
    # 	"weekly": [
    # 		"jammy_app.tasks.weekly"
    # 	]
    # 	"monthly": [
    # 		"jammy_app.tasks.monthly"
    # 	]
}

# Testing
# -------

# before_tests = "jammy_app.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "jammy_app.event.get_events"
# }

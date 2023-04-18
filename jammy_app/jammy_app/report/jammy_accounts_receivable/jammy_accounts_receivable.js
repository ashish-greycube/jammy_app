// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Jammy Accounts Receivable"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "report_date",
			"label": __("Posting Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "finance_book",
			"label": __("Finance Book"),
			"fieldtype": "Link",
			"options": "Finance Book"
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
			}
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			on_change: () => {
				var customer = frappe.query_report.get_filter_value('customer');
				var company = frappe.query_report.get_filter_value('company');
				if (customer) {
					frappe.db.get_value('Customer', customer, ["tax_id", "customer_name", "payment_terms"], function(value) {
						frappe.query_report.set_filter_value('tax_id', value["tax_id"]);
						frappe.query_report.set_filter_value('customer_name', value["customer_name"]);
						frappe.query_report.set_filter_value('payment_terms', value["payment_terms"]);
					});

					frappe.db.get_value('Customer Credit Limit', {'parent': customer, 'company': company},
						["credit_limit"], function(value) {
						if (value) {
							frappe.query_report.set_filter_value('credit_limit', value["credit_limit"]);
						}
					}, "Customer");
				} else {
					frappe.query_report.set_filter_value('tax_id', "");
					frappe.query_report.set_filter_value('customer_name', "");
					frappe.query_report.set_filter_value('credit_limit', "");
					frappe.query_report.set_filter_value('payment_terms', "");
				}
			}
		},
		{
			"fieldname": "party_account",
			"label": __("Receivable Account"),
			"fieldtype": "Link",
			"options": "Account",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company,
						'account_type': 'Receivable',
						'is_group': 0
					}
				};
			}
		},
		{
			"fieldname": "ageing_based_on",
			"label": __("Ageing Based On"),
			"fieldtype": "Select",
			"options": 'Posting Date\nDue Date',
			"default": "Due Date"
		},
		{
			"fieldname": "range1",
			"label": __("Ageing Range 1"),
			"fieldtype": "Int",
			"default": "30",
			"reqd": 1
		},
		{
			"fieldname": "range2",
			"label": __("Ageing Range 2"),
			"fieldtype": "Int",
			"default": "60",
			"reqd": 1
		},
		{
			"fieldname": "range3",
			"label": __("Ageing Range 3"),
			"fieldtype": "Int",
			"default": "90",
			"reqd": 1
		},
		{
			"fieldname": "range4",
			"label": __("Ageing Range 4"),
			"fieldtype": "Int",
			"default": "120",
			"reqd": 1
		},
		{
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname": "payment_terms_template",
			"label": __("Payment Terms Template"),
			"fieldtype": "Link",
			"options": "Payment Terms Template"
		},
		{
			"fieldname": "sales_partner",
			"label": __("Sales Partner"),
			"fieldtype": "Link",
			"options": "Sales Partner"
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname": "territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"options": "Territory"
		},
		{
			"fieldname": "group_by_party",
			"label": __("Group By Customer"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "based_on_payment_terms",
			"label": __("Based On Payment Terms"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "show_future_payments",
			"label": __("Show Future Payments"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "show_delivery_notes",
			"label": __("Show Linked Delivery Notes"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "show_sales_person",
			"label": __("Show Sales Person"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "tax_id",
			"label": __("Tax Id"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "show_remarks",
			"label": __("Show Remarks"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "customer_name",
			"label": __("Customer Name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "payment_terms",
			"label": __("Payment Tems"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "credit_limit",
			"label": __("Credit Limit"),
			"fieldtype": "Currency",
			"hidden": 1
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();

		}
		return value;
	},

	onload: function(report) {
		report.page.add_inner_button(__("Accounts Receivable Summary"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Accounts Receivable Summary', {company: filters.company});
		});
		report.page.add_inner_button(__("Customer Statement"), function() {
			frappe.query_reports["Jammy Accounts Receivable"].customer_statement_data(report, "customer_statement")
		});

		report.page.add_inner_button(__("Customer Letter"), function() {
			frappe.query_reports["Jammy Accounts Receivable"].customer_statement_data(report, "customer_letter_print")
		});		
	},
	print_report: function(report, response, template){
		filters = report.get_values()
		
		if(filters.report_date){
			var flat_date = (filters.report_date).split("-")
			filters.report_date = flat_date[1]+"/"+flat_date[2]+"/"+flat_date[0]
		}

		if(frappe.query_report.data.length > 0){
			var me = this;
			var base_url = frappe.urllib.get_base_url();
			var print_css = frappe.boot.print_css;
			var html = frappe.render_template("head",{
				content: frappe.render_template(template,{   
					"data": response,
					"filters": filters,
					"report_range": {
						"range1": "0-"+String(filters.range1),
						"range2": String(filters.range1+1)+"-"+String(filters.range2),
						"range3": String(filters.range2+1)+"-"+String(filters.range3),
						"range4": String(filters.range3+1)+"-"+String(filters.range4),
						"range5": String(filters.range4+1)+"-Above"
					}
				}),
				title:__(template),
				base_url: base_url,
				print_css: print_css
			});
			
			open_pdf(html)
		}
		else{
			frappe.throw("No Records to print.")
		}
	},	
	customer_statement_data: function(report, template){
		frappe.call({
			method: "jammy_app.jammy_utils.customer_statement",
			args: {
				'data': frappe.query_report.data,
				'filters': report.get_values()
			},
			freeze: true,
   			freeze_message: __("Loading... Please Wait"),
			callback: function(r) {
    			frappe.query_reports["Jammy Accounts Receivable"].print_report(report, r.message, template)
			    frappe.msgprint("Please wait while the document is being prepared for reading.")
			}
		})
	},	
}
open_pdf = function(html) {
	var formData = new FormData();
	formData.append("html", html);
	formData.append("orientation", "Portrait");
	var blob = new Blob([], { type: "text/xml"});
	formData.append("blob", blob);
	var xhr = new XMLHttpRequest();
	xhr.open("POST", '/api/method/frappe.utils.print_format.report_to_pdf');
	xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
	xhr.responseType = "arraybuffer";
	xhr.onload = function(success) {
		if (this.status === 200) {
			var blob = new Blob([success.currentTarget.response], {type: "application/pdf"});
            var objectUrl = URL.createObjectURL(blob);
			window.open(objectUrl);
		}
	};
	xhr.send(formData);
}
erpnext.utils.add_dimensions('Jammy Accounts Receivable', 9);

console.log('ashish')
frappe.query_reports["Accounts Receivable"] = {
	onload: function(report) {
		report.page.add_inner_button(__("Accounts Receivable Summary"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Accounts Receivable Summary', {company: filters.company});
		});
		report.page.add_inner_button(__("Customer Statement"), function() {
			frappe.query_reports["Accounts Receivable"].customer_statement_data(report, "customer_statement")
		});

		report.page.add_inner_button(__("Customer Letter"), function() {
			frappe.query_reports["Accounts Receivable"].customer_statement_data(report, "customer_letter_print")
		});
	}
}    
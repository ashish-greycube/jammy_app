(()=>{console.log("ashish");frappe.query_reports["Accounts Receivable"]={onload:function(e){e.page.add_inner_button(__("Accounts Receivable Summary"),function(){var t=e.get_values();frappe.set_route("query-report","Accounts Receivable Summary",{company:t.company})}),e.page.add_inner_button(__("Customer Statement"),function(){frappe.query_reports["Accounts Receivable"].customer_statement_data(e,"customer_statement")}),e.page.add_inner_button(__("Customer Letter"),function(){frappe.query_reports["Accounts Receivable"].customer_statement_data(e,"customer_letter_print")})}};})();
//# sourceMappingURL=jammy_app.bundle.PCUIEI4O.js.map

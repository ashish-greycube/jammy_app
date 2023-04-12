console.log('ashish')
import "./templates/head.html";
import "./templates/customer_statement.html";
import "./templates/customer_letter_print.html";

// frappe.query_reports["Accounts Receivable"] = {
// 	onload: function(report) {
// 		console.log('imposed')
// 		// report.page.add_inner_button(__("Accounts Receivable Summary"), function() {
// 		// 	var filters = report.get_values();
// 		// 	frappe.set_route('query-report', 'Accounts Receivable Summary', {company: filters.company});
// 		// });
// 		report.page.add_inner_button(__("Customer Statement"), function() {
// 			frappe.query_reports["Accounts Receivable"].customer_statement_data(report, "customer_statement")
// 		});

// 		report.page.add_inner_button(__("Customer Letter"), function() {
// 			frappe.query_reports["Accounts Receivable"].customer_statement_data(report, "customer_letter_print")
// 		});
// 	},
// 	print_report: function(report, response, template){
// 		filters = report.get_values()
		
// 		if(filters.report_date){
// 			var flat_date = (filters.report_date).split("-")
// 			filters.report_date = flat_date[1]+"/"+flat_date[2]+"/"+flat_date[0]
// 		}

// 		if(frappe.query_report.data.length > 0){
// 			var me = this;

// 			var base_url = frappe.urllib.get_base_url();
// 			var print_css = frappe.boot.print_css;
// 			var html = frappe.render_template("head",{
// 				content: frappe.render_template(template,{   
// 					"data": response,
// 					"filters": filters,
// 					"report_range": {
// 						"range1": "0-"+String(filters.range1),
// 						"range2": String(filters.range1+1)+"-"+String(filters.range2),
// 						"range3": String(filters.range2+1)+"-"+String(filters.range3),
// 						"range4": String(filters.range3+1)+"-"+String(filters.range4),
// 						"range5": String(filters.range4+1)+"-Above"
// 					}
// 				}),
// 				title:__(template),
// 				base_url: base_url,
// 				print_css: print_css
// 			});
			
// 			open_pdf(html)
// 		}
// 		else{
// 			frappe.throw("No Records to print.")
// 		}
// 	},

// 	customer_statement_data: function(report, template){
// 		frappe.call({
// 			method: "jammy_app.jammy_utils.customer_statement",
// 			args: {
// 				'data': frappe.query_report.data,
// 				'filters': report.get_values()
// 			},
// 			freeze: true,
//    			freeze_message: __("Loading... Please Wait"),
// 			callback: function(r) {
//     			frappe.query_reports["Accounts Receivable"].print_report(report, r.message, template)
// 			    frappe.msgprint("Please wait while the document is being prepared for reading.")
// 			}
// 		})
// 	}    
// }    

// open_pdf = function(html) {
// 	var formData = new FormData();
// 	formData.append("html", html);
// 	var blob = new Blob([], { type: "text/xml"});
// 	formData.append("blob", blob);
// 	var xhr = new XMLHttpRequest();
// 	xhr.open("POST", '/api/method/frappe.utils.print_format.report_to_pdf');
// 	xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
// 	xhr.responseType = "arraybuffer";
// 	xhr.onload = function(success) {
// 		if (this.status === 200) {
// 			var blob = new Blob([success.currentTarget.response], {type: "application/pdf"});
//             var objectUrl = URL.createObjectURL(blob);
// 			window.open(objectUrl);
// 		}
// 	};
// 	xhr.send(formData);
// }
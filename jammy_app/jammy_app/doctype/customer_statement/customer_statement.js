// Copyright (c) 2020, frappe and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Customer Statement', {
// 	refresh: function(frm) {
// 	},

// 	view_customer_statement(frm){

// 		frappe.call({
// 			method : "jammy_app.jammy_app.doctype.customer_statement.customer_statement.get_html_file",
// 			args: {
// 				'doc': frm.doc
// 			},
// 			callback: function(r){
// 				open_pdf(r.message)
// 			}
// 		});
// 	}
// });

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

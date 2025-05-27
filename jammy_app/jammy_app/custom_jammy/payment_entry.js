
frappe.ui.form.on('Payment Entry', {
	refresh: function(frm) {
		$("button[data-fieldname='get_outstanding_invoices']").hide();
		// frm.trigger('add_custom_outstanding_button')
	},
	setup: function(frm) {
		if (frm.doc.party == "Customer") {
			cur_frm.add_fetch('party','default_sales_partner','sales_partner');
		}
	},
	// party: function(frm) {frm.trigger('add_custom_outstanding_button')},
	// paid_from: function(frm) {frm.trigger('add_custom_outstanding_button')},
	// paid_to: function(frm) {frm.trigger('add_custom_outstanding_button')},
	// paid_amount: function(frm) {frm.trigger('add_custom_outstanding_button')},
	// received_amount: function(frm) {frm.trigger('add_custom_outstanding_button')},
	// add_custom_outstanding_button:function(frm) {
	// 	if(frm.doc.party && frm.doc.paid_from && frm.doc.paid_to && frm.doc.paid_amount && frm.doc.received_amount && frm.doc.docstatus == 0) {
	// 		frm.add_custom_button(__('Get Outstanding Invoice'), function() {
	// 			frm.trigger('_get_outstanding_invoice')
	// 		}, "fa fa-table").addClass("btn-primary");;
	// 	}			
	// },
	get_outstanding_invoice_cf: function(frm) {
		const from_posting_date_default="2018-01-01"
		const today = frappe.datetime.get_today();
		const fields = [
			{fieldtype:"Section Break", label: __("Posting Date")},
			{fieldtype:"Date", label: __("From Date"),
				fieldname:"from_posting_date", default:from_posting_date_default},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_posting_date", default:today},
			{fieldtype:"Section Break", label: __("Due Date")},
			{fieldtype:"Date", label: __("From Date"), fieldname:"from_due_date"},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_due_date"},
			{fieldtype:"Section Break", label: __("Outstanding Amount")},
			{fieldtype:"Float", label: __("Greater Than Amount"),
				fieldname:"outstanding_amt_greater_than", default: 0},
			{fieldtype:"Column Break"},
			{fieldtype:"Float", label: __("Less Than Amount"), fieldname:"outstanding_amt_less_than"},
			{fieldtype:"Section Break"},
			{fieldtype:"Link", label:__("Cost Center"), fieldname:"cost_center", options:"Cost Center",
				"get_query": function() {
					return {
						"filters": {"company": frm.doc.company}
					}
				}
			},
			{fieldtype:"Column Break"},
			{fieldtype:"Section Break"},
			{fieldtype:"Check", label: __("Allocate Payment Amount"), fieldname:"allocate_payment_amount", default:1},
		];

		frappe.prompt(fields, function(filters){
			frappe.flags.allocate_payment_amount = true;
			frm.events.validate_filters_data(frm, filters);
			frm.doc.cost_center = filters.cost_center;

			frm.events.get_outstanding_documents(frm, filters).then(() => {

                console.log("Outstanding documents fetched successfully");

                // loop child table and make array of all SI
				let payment_reference = frm.doc.references
				let reference_invoices = ""
				
				if (payment_reference.length > 0){
					for(let invoice in payment_reference){
						reference_invoices += payment_reference[invoice].reference_name +","
					}
				}

                // do frappe.call and pass the SI array and find in py freight and tarriff
				frappe.call({
					method: "jammy_app.api.get_freight_and_tariff",
					args: {
						invoices : reference_invoices
					}
				}).then(r => {
					//  in frappe.call return fill the freight/tariff value in child table
					let taxes = r.message;
					if (taxes.length > 0){
						for(let invoice in payment_reference){
							for(let tax in taxes){
								if (taxes[tax].sales_invoice == payment_reference[invoice].reference_name){
									payment_reference[invoice].freight_charges = taxes[tax].freight_value
									payment_reference[invoice].custom_tariff = taxes[tax].tariff_value
								}
							}
						}
					}
				})

            }
            );

		}, __("Filters"), __("Get Outstanding Documents"));
	},	
})

frappe.ui.form.on('Payment Entry Reference', {
	refresh(frm) {
		cur_frm.add_fetch('reference_name','total_taxes_and_charges','freight_charges');
		cur_frm.add_fetch('reference_name','base_total_taxes_and_charges','freight_charges');
	}
})
function create_je(frm) {
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Custom Employee Salary Component',
            'filters': {
                'name': frm.doc.salary_component
            },
            'fieldname': ['component_name', 'expense_account', 'payable_account']
        },
        callback: function (data) {
            ccco_params.je = populate_je_obj(frm, data);
        }
    });
}

function populate_je_obj(frm, data) {
    let je = {};
    let accounts = [
        {
            "doctype": "Journal Entry Account",
            "account": data.message.payable_account,
            "party": frm.doc.customer,
            "party_type": "customer",
            "debit": 0,
            "credit": frm.doc.gross_pay,
            "credit_in_account_currency": frm.doc.gross_pay,
            "user_remark": cur_frm.docname
        },

        {
            "doctype": "Journal Entry Account",
            "account": data.message.expense_account,
            "debit": frm.doc.gross_pay,
            "credit": 0,
            "debit_in_account_currency": frm.doc.gross_pay,
            "user_remark": cur_frm.docname
        }
    ];
    je["doctype"] = "Journal Entry";
    je["posting_date"] = frappe.datetime.add_days(frm.doc.process_date, 0),
    je["accounts"] = accounts;
    return je;
}

function submit_je(frm) {
    ccco_params.je["remark"] = cur_frm.docname;
    frappe.db.insert(ccco_params.je)
        .then(function (doc) {
            frappe.call({
                "method": "frappe.client.submit",
                "args": {
                    "doc": doc
                },
                "callback": (r) => {
                    console.log(r);
                }
            });
        });
}
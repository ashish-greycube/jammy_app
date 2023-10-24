// cur_frm.add_fetch('item_code', 'pcs_ctn', 'pcs_ctn');
frappe.ui.form.on("Purchase Order", {
	schedule_date: function(frm) {
		$.each(frm.doc.items || [], function(i, d) {
			d.schedule_date = frm.doc.schedule_date;
		});
		refresh_field("items");
	},    
    validate:function (frm) {
        if (frm.doc.transaction_date) {
            for (var i = 0; i < cur_frm.doc.items.length; i++) {
                cur_frm.doc.items[i].transaction_date = cur_frm.doc.transaction_date
            }
            cur_frm.refresh_field('items')          
        }

        if (cur_frm.doc.purchase_order_no) {
            for (var i = 0; i < cur_frm.doc.items.length; i++) {
                cur_frm.doc.items[i].purchase_order_no = cur_frm.doc.purchase_order_no
            }
            cur_frm.refresh_field('items')          
        }
       
    },
    before_save: async function (frm) {
        await call_main(frm)
        cur_frm.refresh_field('items')
    }
})

frappe.ui.form.on("Purchase Order Item", {
	pcs_ctn: function(frm, cdt, cdn) {
        set_cartons(frm, cdt, cdn);

	},

	qty: function(frm, cdt, cdn) {
        set_cartons(frm, cdt, cdn);
	}
});

var set_cartons = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.pcs_ctn) {
		var qty = row.qty || 1;
		var cartons = (flt(qty) / flt(row.pcs_ctn));
		frappe.model.set_value(cdt, cdn, "cartons", cartons);
	}
}
async function call_main(frm) {
    for (var i = 0; i < frm.doc.items.length; i++) {
        if (frm.doc.items[i].item_name==undefined || frm.doc.items[i].item_name=='' || frm.doc.items[i].description==undefined  || frm.doc.items[i].description==''){
   
            if (!frm.doc.schedule_date) {
                frappe.throw(__('Required By Date is mandatory..'))
            }
            if (!frm.doc.warehouse) {
                frappe.throw(__('Accepted Warehouse is mandatory..'))
            }            
            if (i==0) {
               frappe.show_alert(__("Custom item details fetch has started..."), Math.floor(frm.doc.items.length/5));
            }
            // let values = await get_closed_taks(frm.doc.items[i].item_code)
            let values = await get_item_details(frm,frm.doc.items[i])
            let custom_values=await get_custom_item_details(frm.doc.items[i].item_code)
            frm.doc.items[i].pcs_ctn=custom_values.pcs_ctn
            frm.doc.items[i].cartons=(flt(values.qty) / flt(frm.doc.items[i].pcs_ctn));
            // frm.doc.items[i].item_name=values.item_name
            // frm.doc.items[i].description=values.description
            // console.log(frm.doc.items[i],'frm.doc.items[i]')
            if (i==(frm.doc.items.length-1)) {
                frappe.show_alert(__("Custom item details fetch is complete..."), 2);
                
            }            
        }
    }
    cur_frm.refresh_field('items')

}

// function get_closed_taks(item_code) {
//     return new Promise((resolve, reject) => {
//         frappe.db.get_value('Item', item_code, ['item_name', 'description'])
//         .then(r => {
//             let values = r.message;
//             console.log('values',values)
//             return resolve(values)
//         })
//     })
// }

function get_custom_item_details(item_code) {
    return new Promise((resolve, reject) => {
        frappe.db.get_value('Item', item_code, ['pcs_ctn'])
        .then(r => {
            let values = r.message;
            return resolve(values)
        })
    })
}

function get_item_details(frm, item, overwrite_warehouse=false) {
    return new Promise((resolve, reject) => {
		frm.call({
			method: "erpnext.stock.get_item_details.get_item_details",
			child: item,
			args: {
				args: {
					item_code: item.item_code,
                    is_old_subcontracting_flow:frm.doc.is_old_subcontracting_flow,
                    supplier:frm.doc.supplier,
					currency: frm.doc.currency || frappe.defaults.get_default('Currency'),
					conversion_rate: frm.doc.conversion_rate,
					price_list: frm.doc.buying_price_list || frappe.defaults.get_default('buying_price_list'),
                    price_list_currency:frm.doc.currency || frappe.defaults.get_default('Currency'),
                    plc_conversion_rate: frm.doc.plc_conversion_rate,
                    company: frm.doc.company,
                    is_subcontracted:frm.doc.is_subcontracted,
                    ignore_pricing_rule:frm.doc.ignore_pricing_rule,
					doctype: frm.doc.doctype,
					name: frm.doc.name,
					qty: item.qty || 1,
					conversion_factor: item.conversion_factor,
                    weight_per_unit:item.weight_per_unit,
                    weight_uom:item.weight_uom,
                    tax_category:frm.doc.tax_category,
                    child_docname:item.child_docname,
				     // barcode:null,
                    // update_stock:0,
                    // is_pos:0,
                    // is_return:0,
                    // pos_profile:"",

                    // from_warehouse: item.from_warehouse,
					// warehouse: item.warehouse,
                    // include_child_warehouses: true,					
				},
				// overwrite_warehouse: overwrite_warehouse
			},
			callback: function(r) {
				const d = item;
				const exclude_fields_to_update = ['warehouse','purchase_order_no'];
				if(!r.exc) {
					$.each(r.message, function(k, v) {
						if(!d[k] || in_list(exclude_fields_to_update, k)) d[k] = v;
					});
                    if (frm.doc.warehouse) {
                        // if (!d['warehouse']) {
                            d['warehouse'] =   frm.doc.warehouse 
                        // }
                       
                    }
                    if (frm.doc.purchase_order_no) {
                        d['purchase_order_no'] =   frm.doc.purchase_order_no 
                    }                    
                    return resolve(r.message)
				}
			}
		})
    })
}
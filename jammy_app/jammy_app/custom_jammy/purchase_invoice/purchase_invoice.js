// frappe.ui.form.on('Purchase Invoice',{
// 	refresh:function(frm){	
// 			console.log("---------------------");
// 			$.each(frm.doc.items, function(index,row){
// 				console.log("=======test========")
// 				frappe.db.get_value('Purchase Receipt Item', { name: row.purchase_receipt_item },'batch_no', function(data){
//  				row.batch_no= data.batch_no})

//  			});
			
// 			refresh_field('items')	
// 	},
// });

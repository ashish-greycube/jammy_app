frappe.ui.form.on('Terms and Conditions',{
	is_default:function(frm){
		if (frm.doc.is_default){
			frappe.db.get_value('Terms and Conditions', {'is_default': 1,'name':['!=',frm.doc.name]}, 'name', (r) => {
				if (r.name){
					frm.set_value('is_default',0)
					frappe.throw("<b>Already exist Terms and Conditions </b>")
				}
			});
		}
	}
});
// Copyright (c) 2023, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shipping Easy Order", {
  refresh: function (frm) {
    frappe.timeout(1).then(() => {
      frm.set_value(
        "json_data",
        JSON.stringify(JSON.parse(frm.doc.json_data || "{}"), null, 4)
      );
    });
  },
});

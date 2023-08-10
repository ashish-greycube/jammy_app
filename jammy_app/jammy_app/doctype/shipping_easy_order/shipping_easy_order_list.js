frappe.listview_settings["Shipping Easy Order"] = {
  onload: function (listview) {
    listview.page.add_menu_item(__("Fetch Orders"), function () {
      frappe.call({
        method:
          "jammy_app.jammy_app.doctype.shipping_easy_order.shipping_easy_order.sync_orders",
        args: {},
        freeze: true,
        freeze_message: __("Fetching orders."),
        callback: (r) => {
          frappe.show_alert("Fetched Orders");
        },
      });
    });
  },
};

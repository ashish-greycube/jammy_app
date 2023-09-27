frappe.listview_settings["Shipping Easy Order"] = {
  onload: function (listview) {
    listview.page.add_menu_item(__("Sync Orders"), function () {
      frappe.prompt(
        [
          {
            fieldname: "from_date",
            label: "Sync Orders from Date",
            fieldtype: "Date",
            reqd: 1,
          },
        ],
        function (values) {
          frappe.call({
            method:
              "jammy_app.jammy_app.doctype.shipping_easy_order.shipping_easy_order.sync_orders",
            args: { from_date: values.from_date },
            freeze: true,
            freeze_message: __("Syncing orders."),
            callback: (r) => {
              frappe.show_alert("Synced Orders");
            },
          });
        }
      );
    });

    listview.page.add_menu_item(__("Fetch Order"), function () {
      frappe.prompt(
        [
          {
            fieldname: "order_id",
            label: "Order Id",
            fieldtype: "Data",
            reqd: 1,
          },
        ],
        function (values) {
          frappe.call({
            method:
              "jammy_app.jammy_app.doctype.shipping_easy_order.shipping_easy_order.fetch_order",
            args: { order_id: values.order_id },
            freeze: true,
            freeze_message: __("Fetching Order"),
            callback: (r) => {
              frappe.show_alert("Order has been fetched.");
            },
          });
        }
      );
    });
  },
};

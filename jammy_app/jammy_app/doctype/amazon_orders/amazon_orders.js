// Copyright (c) 2025, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Amazon Orders', {

	refresh: function (frm) {
		if (frm.missing_orders_dt) {
			frm.missing_orders_dt.refresh([])
		}


		frm.add_custom_button(
			__("Import Missing Orders"),
			function () {
				return frappe.call({
					doc: frm.doc,
					method: "import_missing_orders",
					freeze: true,
					freeze_message: __("Please wait while we import Orders..."),
					callback: function (r) {
						frappe.msgprint('Imported missing Orders.')
					},
				});

			},
		);

		frm.add_custom_button(
			__("Get Missing Orders"),
			function () {
				return frappe.call({
					doc: frm.doc,
					method: "get_missing_orders",
					callback: function (r) {
						// console.log(r.message);
						const $wrapper = frm.get_field("missing_orders_html").$wrapper;
						const summary_wrapper = $(`<div class="summary_wrapper">`).appendTo($wrapper);
						frm.events.render_datatable(frm, r.message, summary_wrapper);
					},
				});

			},
		);
	},


	render_datatable(frm, data, summary_wrapper) {
		const columns = frm.events.get_order_columns(data[0]);

		if (!frm.missing_orders_dt) {
			const datatable_options = {
				columns: columns,
				data: data.slice(1),
				dynamicRowHeight: true,
				inlineFilters: true,
				layout: "fixed",
				cellHeight: 35,
				noDataMessage: __("No Data"),
				disableReorderColumn: true,
			};
			frm.missing_orders_dt = new frappe.DataTable(
				summary_wrapper.get(0),
				datatable_options,
			);
		} else {
			frm.missing_orders_dt.refresh(data.slice(1), columns);
		}
	},


	get_order_columns(columns) {
		return columns
			.map(t => ({
				name: t,
				id: t,
				width: 150,
				content: t,
				align: "left"
			}));
	},
});

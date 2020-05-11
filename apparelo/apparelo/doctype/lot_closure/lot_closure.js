// Copyright (c) 2020, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lot Closure', {
	// refresh: function(frm) {

	// }
	verify_lot_status:function(frm) {
		const set_fields =['rm_item_code','supplier','supplied_qty','consumed_qty','difference','po','pr'];
		frappe.call({
			method: "apparelo.apparelo.doctype.lot_closure.lot_closure.get_lot_closure_details",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('lot_closure_details', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('lot_closure_details');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('lot_closure_details');
			}
		});
	},
	get_lot_closure_items:function(frm) {
		const set_fields =['item_code','bal_qty','warehouse','target_warehouse','stock_uom'];
		frappe.call({
			method: "apparelo.apparelo.doctype.lot_closure.lot_closure.get_lot_closure_items",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('lot_closure_items', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('lot_closure_items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('lot_closure_items');
			}
		});
	},
});

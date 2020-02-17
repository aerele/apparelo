// Copyright (c) 2020, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lot Closure', {
	check:function(frm) {
		const set_fields =['item','supplier','outward_quantity','inward_quantity','difference_'];
		frappe.call({
			method: "apparelo.apparelo.doctype.lot_closure.lot_closure.check_lot",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('surplus_item_details', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('itesurplus_item_detailsms');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('surplus_item_details');
			}
		});
	}
});

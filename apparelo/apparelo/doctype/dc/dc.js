// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('DC', {
	onload: function(frm) {
		frm.set_query("supplier", function() {
			return {
				query: "apparelo.apparelo.doctype.dc.dc.get_supplier",
				filters: {
					"supplier_process.processes": frm.doc.process_1
				}
			};
		});
	},
	get_items:function(frm) {
		const set_fields =['item_code','available_quantity','uom'];
		frappe.call({
			method: "apparelo.apparelo.doctype.dc.dc.get_ipd_item",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('items', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('items');
			}
		});
	},
	get_return_item: function(frm) {
		const set_fields = ['item_code','uom','quantity'];
		frappe.call({
			method: "apparelo.apparelo.doctype.dc.dc.item_return",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('return_materials', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('return_materials');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('return_materials');
			}
		});
	},
});

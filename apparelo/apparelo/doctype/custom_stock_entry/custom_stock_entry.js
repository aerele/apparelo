// Copyright (c) 2021, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custom Stock Entry', {
	delete_unavailable_items:function(frm){
		const set_fields = ['item_code','qty','uom'];
		frappe.call({
			method: "apparelo.apparelo.doctype.custom_stock_entry.custom_stock_entry.delete_unavailable_items",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('stock_entry_items', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('stock_entry_items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('stock_entry_items');
			}
		});
	},
	make_entry:function(frm){
		const set_fields = ['item_code', 'uom', 'qty'];
		frappe.call({
			method: "apparelo.apparelo.doctype.custom_stock_entry.custom_stock_entry.make_entry",
			freeze: true,
			args: {
				doc: frm.doc
			},
			callback: function(r) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var item = frm.add_child('stock_entry_items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('stock_entry_items');
			}
		});

	},
	get_items: function(frm) {
		const set_fields = ['item_code', 'uom'];
		frappe.call({
			method: "apparelo.apparelo.doctype.custom_stock_entry.custom_stock_entry.get_inward_item",
			freeze: true,
			args: {
				doc: frm.doc
			},
			callback: function(r) {
				if(r.message) {
					frm.set_value('stock_entry_items', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('stock_entry_items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('stock_entry_items');
			}
		});

	}
});

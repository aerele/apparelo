// Copyright (c) 2020, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRN', {
	onload: function(frm) {
		frm.set_query("supplier", function() {
			return {
				query: "apparelo.apparelo.doctype.grn.grn.get_supplier",
			};
		});
		frm.set_query("lot", function() {
			return {
				query: "apparelo.apparelo.doctype.grn.grn.get_Lot",
				filters: {
					"supplier": frm.doc.supplier
				}
			};
		});
		frm.set_query("against_document", function() {
				return {
					query: "apparelo.apparelo.doctype.grn.grn.get_type",
					filters: {
						"supplier": frm.doc.supplier,
						"type": frm.doc.against_type,
						"lot": frm.doc.lot
					}
				};
		});
	},
	get_items: function(frm) {
		const set_fields = ['item_code','uom','qty','pf_item_code'];
		frappe.call({
			method: "apparelo.apparelo.doctype.grn.grn.get_items",
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


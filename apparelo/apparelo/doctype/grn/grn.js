// Copyright (c) 2020, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRN', {
	onload: function(frm) {
		frm.set_df_property("select_helper","options",['','Copy Over','Divide Total Quantity'].join('\n'))
		frm.set_df_property("from_field","options",['Expected Qty','Received Qty','Rejected Qty'].join('\n'))
		frm.set_df_property("to_field","options",['Expected Qty','Received Qty','Rejected Qty'].join('\n'))
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
	copy_over:function(frm){
		const set_fields = ['pf_item_code','item_code','qty','received_qty','rejected_qty','uom','secondary_qty','secondary_uom'];
		frappe.call({
			method: "apparelo.apparelo.doctype.grn.grn.duplicate_values",
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
	attribute: function(frm)
	{
		frappe.call({
			method: "apparelo.apparelo.doctype.grn.grn.get_attribute_value",
			freeze: true,
			args: {attribute: frm.doc.attribute},
			callback: function(r) {
			  if(r.message) {
				frm.set_df_property("attribute_value","options",r.message);
			  }
			}
		  });
	},
	delete_unavailable_return_items:function(frm){
		const set_fields = ['pf_item_code','item_code','qty','received_qty','rejected_qty','uom','secondary_qty','secondary_uom'];
		frappe.call({
			method: "apparelo.apparelo.doctype.grn.grn.delete_unavailable_return_items",
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
	get_items: function(frm) {
		const set_fields = ['item_code','uom','qty','pf_item_code',"secondary_uom"];
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
	divide_total_quantity: function(frm){
		const set_fields = ['item_code','uom','qty','received_qty','pf_item_code',"secondary_uom"];
		frappe.call({
			method: "apparelo.apparelo.doctype.grn.grn.divide_total_quantity",
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
	}

});


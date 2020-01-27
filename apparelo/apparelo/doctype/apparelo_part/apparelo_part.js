// Copyright (c) 2020, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Apparelo Part', {
	onload: function(frm) {
		frm.set_query("combined_parts", function() {
			return {
				filters: {
					"is_combined": 0
				}
			};
		});
	},
	get_combined_parts:function(frm){
		frappe.call({
			method: "apparelo.apparelo.doctype.apparelo_part.apparelo_part.get_combined_parts",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('part_name',r.message.final_part);
				}
			}
		})
	}
});

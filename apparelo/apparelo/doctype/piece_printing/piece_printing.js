// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Piece Printing', {
	onload: function(frm) {
		frm.set_query("item", function() {
			return {
				filters: {
					"item_group":"Products",
					"has_variants":1
				}
			};
		});
	},
});

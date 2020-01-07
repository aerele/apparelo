// Copyright (c) 2020, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRN', {
	onload: function(frm) {
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
				query: "apparelo.apparelo.doctype.grn.grn.get_DC",
				filters: {
					"supplier": frm.doc.supplier
				}
			};
		});
	},
});

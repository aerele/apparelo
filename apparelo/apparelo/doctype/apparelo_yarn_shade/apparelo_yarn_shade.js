// Copyright (c) 2020, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Apparelo Yarn Shade', {
	// refresh: function(frm) {

	// }

	get_combined_yarn:function(frm){
		frappe.call({
			method: "apparelo.apparelo.doctype.apparelo_yarn_shade.apparelo_yarn_shade.get_yarn_shade",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('yarn_shade',r.message.final_yarn_shade);
				}
			}
		})
	}
});

// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Knitting', {
	onload: function(frm) {
		frm.set_query("yarn", "apparelo_yarn_ratio", function() {
        return {
            filters: {
                "variant_of":"Yarn",
            }
        };
    });

	}
});

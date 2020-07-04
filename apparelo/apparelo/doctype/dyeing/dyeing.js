// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dyeing', {
	get_field_values:function(frm){
		const set_fields =['yarn_shade','colour'];
		frappe.call({
			method: "apparelo.apparelo.doctype.dyeing.dyeing.get_field_values",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('colour_shade_mapping', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('colour_shade_mapping');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('colour_shade_mapping');
			}
		});
	}
});

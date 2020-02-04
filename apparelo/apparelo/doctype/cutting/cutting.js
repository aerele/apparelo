// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt
{% include 'apparelo/apparelo/common_fields.js' %};
frappe.ui.form.on('Cutting', {
	get_size_combination:function(frm){
		const set_fields =['part','size'];
		frappe.call({
			method: "apparelo.apparelo.doctype.cutting.cutting.get_part_size_combination",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('details', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('details');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('details');
			}
		});
	},

	get_colour_combination:function(frm){
		const set_fields =['part','colour','style'];
		frappe.call({
			method: "apparelo.apparelo.doctype.cutting.cutting.get_part_colour_combination",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('colour_mapping', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('colour_mapping');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('colour_mapping');
			}
		});
	}
});

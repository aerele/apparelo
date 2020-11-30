// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt
{% include 'apparelo/apparelo/common_fields.js' %};
frappe.ui.form.on('Item Production Detail', {
  submit_internal_processes: function(frm) {
    console.log(frappe.session.user)
    frappe.call({
			method: "submit_all_process_records",
			freeze: true,
			doc: frm.doc,
			callback: function(r) {
				frm.reload_doc();
			}
		});
  },
  swap_colours: function(frm) {
	const set_fields = ['input_item','input_index','process_name','process_record','ipd_name','ipd_process_index','previous_process'];
    frappe.call({
			method: "apparelo.apparelo.doctype.item_production_detail.item_production_detail.create_process_records",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('processes', []);
					$.each(r.message[0], function(i, d) {
						var item = frm.add_child('processes');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
					frm.set_value('colour', []);
					$.each(r.message[1], function(i,d) {
						var item = frm.add_child('colour');
						item['colour'] = d;
					});
				}
				refresh_field('processes');
				refresh_field('colour');
			}
		});
  }
});

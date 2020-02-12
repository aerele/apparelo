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
  }
});

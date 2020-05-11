// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lot Creation', {
	onload: function(frm) {
		frm.set_query('item_production_detail', function(doc) {
			return {
				filters: {
					"docstatus": 1
				}
			}
		});
	},
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Work Order': 'Work Order',
			'Material Request': 'Material Request',
		};

		frm.fields_dict['po_items'].grid.get_field('warehouse').get_query = function(doc) {
			return {
				filters: {
					company: doc.company
				}
			}
		}

		frm.set_query('for_warehouse', function(doc) {
			return {
				filters: {
					company: doc.company
				}
			}
		});

		frm.fields_dict['po_items'].grid.get_field('item_code').get_query = function(doc) {
			return {
				query: "erpnext.controllers.queries.item_query",
				filters:{
					'is_stock_item': 1,
				}
			}
		}

		frm.fields_dict['po_items'].grid.get_field('bom_no').get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			if (d.item_code) {
				return {
					query: "erpnext.controllers.queries.bom",
					filters:{'item': cstr(d.item_code)}
				}
			} else frappe.msgprint(__("Please enter Item first"));
		}

		frm.fields_dict['mr_items'].grid.get_field('warehouse').get_query = function(doc) {
			return {
				filters: {
					company: doc.company
				}
			}
		}
	},
	refresh: function(frm) {

		if (frm.doc.docstatus === 1 && frm.doc.mr_items
			&& !in_list(['Material Requested', 'Completed'], frm.doc.status)) {
			frm.add_custom_button(__("Material Request"), ()=> {
				frm.trigger("make_material_request");
			}, __('Create'));
		}
		frm.page.set_inner_btn_group_as_primary(__('Create'));
		frm.trigger("material_requirement");

		const projected_qty_formula = ` <table class="table table-bordered" style="background-color: #f9f9f9;">
			<tr><td style="padding-left:25px">
				<div>
				<h3>
					<a href = "https://erpnext.com/docs/user/manual/en/stock/projected-quantity">
						${__("Projected Quantity Formula")}
					</a>
				</h3>
					<div>
						<h3 style="font-size: 13px">
							(Actual Qty + Planned Qty + Requested Qty + Ordered Qty) - (Reserved Qty + Reserved for Production + Reserved for Subcontract)
						</h3>
					</div>
					<br>
					<div>
						<ul>
							<li>
								${__("Actual Qty: Quantity available in the warehouse.")}
							</li>
							<li>
								${__("Planned Qty: Quantity, for which, Work Order has been raised, but is pending to be manufactured.")}
							</li>
							<li>
								${__('Requested Qty: Quantity requested for purchase, but not ordered.')}
							</li>
							<li>
								${__('Ordered Qty: Quantity ordered for purchase, but not received.')}
							</li>
							<li>
								${__("Reserved Qty: Quantity ordered for sale, but not delivered.")}
							</li>
							<li>
								${__('Reserved Qty for Production: Raw materials quantity to make manufacturing items.')}
							</li>
							<li>
								${__('Reserved Qty for Subcontract: Raw materials quantity to make subcontracted items.')}
							</li>
						</ul>
					</div>
				</div>
			</td></tr>
		</table>`;

		set_field_options("projected_qty_formula", projected_qty_formula);
	},
	make_material_request: function(frm) {

		frappe.confirm(__("Do you want to submit the material request"),
			function() {
				frm.events.create_material_request(frm, 1);
			},
			function() {
				frm.events.create_material_request(frm, 0);
			}
		);
	},

	create_material_request: function(frm, submit) {
		frm.doc.submit_material_request = submit;

		frappe.call({
			method: "make_material_request",
			freeze: true,
			doc: frm.doc,
			callback: function(r) {
				frm.reload_doc();
			}
		});
	},
	add_new_location:function(frm) {
		frappe.call({
			method: "apparelo.apparelo.doctype.lot_creation.lot_creation.create_new_warehouse",
			freeze: true,
			args: {doc: frm.doc}
		});
	},
	get_items:function(frm) {
		const set_fields =['item_code','bom_no'];
		frappe.call({
			method: "apparelo.apparelo.doctype.lot_creation.lot_creation.get_ipd_item",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('po_items', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('po_items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('po_items');
			}
		});
	},
	get_items_for_mr: function(frm) {
		const set_fields = ['actual_qty', 'item_code','item_name', 'description', 'uom',
			'min_order_qty', 'quantity', 'sales_order', 'warehouse', 'projected_qty', 'material_request_type', 'req_by_date'];
		frappe.call({
			method: "apparelo.apparelo.doctype.lot_creation.lot_creation.get_base_materials",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('mr_items', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('mr_items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('mr_items');
			}
		});
		frappe.call({
			method: "apparelo.apparelo.doctype.lot_creation.lot_creation.cloth_qty",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('cloth_quantity', r.message);
				}
				refresh_field('cloth_quantity');
			}
		});
	},
	for_warehouse: function(frm) {
		if (frm.doc.mr_items) {
			frm.trigger("get_items_for_mr");
		}
	},
});


frappe.ui.form.on("Lot Creation Plan Item", {
	item_code: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.item_code) {
			frappe.call({
				method: "erpnext.manufacturing.doctype.production_plan.production_plan.get_item_data",
				args: {
					item_code: row.item_code
				},
				callback: function(r) {
					for (let key in r.message) {
						frappe.model.set_value(cdt, cdn, key, r.message[key]);
					}
				}
			});
		}
	}
});

frappe.ui.form.on("Material Request Plan Item", {
	warehouse: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.warehouse && row.item_code && frm.doc.company) {
			frappe.call({
				method: "erpnext.manufacturing.doctype.production_plan.production_plan.get_bin_details",
				args: {
					row: row,
					company: frm.doc.company,
					for_warehouse: row.warehouse
				},
				callback: function(r) {
					let {projected_qty, actual_qty} = r.message;

					frappe.model.set_value(cdt, cdn, 'projected_qty', projected_qty);
					frappe.model.set_value(cdt, cdn, 'actual_qty', actual_qty);
				}
			})
		}
	}
});
# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _, msgprint
from frappe.model.document import Document
from six import string_types, iteritems
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from erpnext.manufacturing.doctype.production_plan.production_plan import get_exploded_items, get_subitems, get_bin_details, get_material_request_items
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil


class LotCreation(Document):
	def on_submit(self):
		default_company = frappe.db.get_single_value(
		    'Global Defaults', 'default_company')
		abbr = frappe.db.get_value("Company", f"{default_company}", "abbr")
		create_parent_warehouse(self, abbr)
		create_warehouse(self, abbr)

	def make_material_request(self):
		'''Create Material Requests grouped by Sales Order and Material Request Type'''
		material_request_list = []
		material_request_map = {}

		for item in self.mr_items:
			item_doc = frappe.get_cached_doc('Item', item.item_code)

			material_request_type = item.material_request_type or item_doc.default_material_request_type

			# key for Sales Order:Material Request Type:Customer
			key = '{}:{}:{}'.format(
			    item.sales_order, material_request_type, item_doc.customer or '')
			schedule_date = add_days(nowdate(), cint(item_doc.lead_time_days))

			if not key in material_request_map:
				# make a new MR for the combination
				material_request_map[key] = frappe.new_doc("Material Request")
				material_request = material_request_map[key]
				material_request.update({
					"transaction_date": nowdate(),
					"status": "Draft",
					"company": frappe.db.get_single_value('Global Defaults', 'default_company'),
					"requested_by": frappe.session.user,
					'material_request_type': material_request_type,
					'customer': item_doc.customer or ''
				})
				material_request_list.append(material_request)
			else:
				material_request = material_request_map[key]

			# add item
			default_company = frappe.db.get_single_value(
			    'Global Defaults', 'default_company')
			abbr = frappe.db.get_value("Company", f"{default_company}", "abbr")
			material_request.append("items", {
				"item_code": item.item_code,
				"qty": item.quantity,
				"schedule_date": schedule_date,
				"warehouse": f'{self.name} - {abbr}',
				"sales_order": item.sales_order,
				'lot_creation': self.name,
				'material_request_plan_item': item.name,
				"project": frappe.db.get_value("Sales Order", item.sales_order, "project")
					if item.sales_order else None
			})

		for material_request in material_request_list:
			# submit
			material_request.flags.ignore_permissions = 1
			material_request.run_method("set_missing_values")

			if self.get('submit_material_request'):
				material_request.submit()
			else:
				material_request.save()

		frappe.flags.mute_messages = False

		if material_request_list:
			material_request_list = ["""<a href="#Form/Material Request/{0}">{1}</a>""".format(m.name, m.name)
				for m in material_request_list]
			msgprint(_("{0} created").format(comma_and(material_request_list)))
		else:
			msgprint(_("No material request created"))


@frappe.whitelist()
def get_items_for_material_requests(doc, ignore_existing_ordered_qty=None):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))

	doc['mr_items'] = []
	po_items = doc.get('po_items') if doc.get('po_items') else doc.get('items')
	if not po_items:
		frappe.throw(
		    _("Items are required to pull the raw materials which is associated with it."))

	company = doc.get('company')
	warehouse = doc.get('for_warehouse')

	if not ignore_existing_ordered_qty:
		ignore_existing_ordered_qty = 1

	so_item_details = frappe._dict()
	for data in po_items:
		planned_qty = data.get('required_qty') or data.get('planned_qty')
		ignore_existing_ordered_qty = 1
		warehouse = data.get("warehouse") or warehouse

		item_details = {}
		if data.get("bom") or data.get("bom_no"):
			if data.get('required_qty'):
				bom_no = data.get('bom')
				include_non_stock_items = 1
				include_subcontracted_items = 1
				# if data.get('include_exploded_items') else 0
			else:
				bom_no = data.get('bom_no')
				include_subcontracted_items = 1
				include_non_stock_items = 1

			if bom_no:
				if include_subcontracted_items:
					# fetch exploded items from BOM
					item_details = get_exploded_items(item_details,
						company, bom_no, include_non_stock_items, planned_qty=planned_qty)
				else:
					item_details = get_subitems(doc, data, item_details, bom_no, company,
						include_non_stock_items, include_subcontracted_items, 1, planned_qty=planned_qty)
		elif data.get('item_code'):
			item_master = frappe.get_doc('Item', data['item_code']).as_dict()
			purchase_uom = item_master.purchase_uom or item_master.stock_uom
			conversion_factor = 0
			for d in item_master.get("uoms"):
				if d.uom == purchase_uom:
					conversion_factor = d.conversion_factor

			item_details[item_master.name] = frappe._dict(
				{
					'item_name': item_master.item_name,
					'default_bom': doc.bom,
					'purchase_uom': purchase_uom,
					'default_warehouse': item_master.default_warehouse,
					'min_order_qty': item_master.min_order_qty,
					'default_material_request_type': item_master.default_material_request_type,
					'qty': planned_qty or 1,
					'is_sub_contracted': item_master.is_subcontracted_item,
					'item_code': item_master.name,
					'description': item_master.description,
					'stock_uom': item_master.stock_uom,
					'conversion_factor': conversion_factor,
				}
			)

		sales_order = doc.get("sales_order")

		for item_code, details in iteritems(item_details):
			so_item_details.setdefault(sales_order, frappe._dict())
			if item_code in so_item_details.get(sales_order, {}):
				so_item_details[sales_order][item_code]['qty'] = so_item_details[sales_order][item_code].get(
				    "qty", 0) + flt(details.qty)
			else:
				so_item_details[sales_order][item_code] = details

	mr_items = []
	for sales_order, item_code in iteritems(so_item_details):
		item_dict = so_item_details[sales_order]
		for details in item_dict.values():
			bin_dict = get_bin_details(details, doc.company, warehouse)
			bin_dict = bin_dict[0] if bin_dict else {}

			if details.qty > 0:
				items = get_material_request_items(details, sales_order, company,
					ignore_existing_ordered_qty, warehouse, bin_dict)
				if items:
					mr_items.append(items)
	for item in mr_items:
		if item['uom'] == 'Nos':
			if round(item['quantity'] + (item['quantity'] * float(doc.get('percentage')))/100) < (item['quantity'] + (item['quantity'] * float(doc.get('percentage')))/100):
				item['quantity']=round(item['quantity'] + (item['quantity'] * float(doc.get('percentage')))/100) + 1
			else:
				item['quantity']=round(item['quantity'] +(item['quantity'] * float(doc.get('percentage')))/100)
		else:
			item['quantity']=item['quantity'] +(item['quantity'] * float(doc.get('percentage')))/100

	if not mr_items:
		frappe.msgprint(_("""As raw materials projected quantity is more than required quantity, there is no need to create material request.
			Still if you want to make material request, kindly enable <b>Ignore Existing Projected Quantity</b> checkbox"""))

	return mr_items

@frappe.whitelist()
def get_ipd_item(doc):
	if isinstance(doc, string_types):
		doc=frappe._dict(json.loads(doc))
	doc['po_items']=[]
	po_items=[]
	item_production_detail=doc.get('item_production_detail')
	item_template=frappe.db.get_value("Item Production Detail", {
	                                  'name': item_production_detail}, "item")
	item_code=frappe.db.get_all("Item", fields = ["item_code"], filters = {
	                            "variant_of": item_template})
	for item in item_code:
		po_items.append({"item_code": item.get("item_code"), "bom_no": get_item_details(
		    item.get("item_code")).get("bom_no")})
	return po_items

def create_parent_warehouse(self,abbr):
	if not frappe.db.exists("Warehouse", f'{self.name} - {abbr}'):
		frappe.get_doc({
			"doctype": "Warehouse",
			"warehouse_name": self.name,
			"is_group": 1,
			"parent_warehouse": f"{name} - {abbr}"
			}).save()

def create_warehouse(self, abbr):
	for location in self.location:
		if not frappe.db.exists("Warehouse", f"{self.name}-{location.location} - {abbr}"):
			frappe.get_doc({
				"doctype": "Warehouse",
				"warehouse_name": f"{self.name}-{location.location}",
				"is_group": 0,
				"parent_warehouse": f"{self.name} - {abbr}"
				}).save()
		if not frappe.db.exists("Warehouse", f"{self.name}-{location.location} Mistake - {abbr}"):
			frappe.get_doc({
				"doctype": "Warehouse",
				"warehouse_name": f"{self.name}-{location.location} Mistake",
				"is_group": 0,
				"parent_warehouse": f"{self.name} - {abbr}"
				}).save()

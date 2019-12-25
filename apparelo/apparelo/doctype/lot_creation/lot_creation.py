# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _,msgprint
from frappe.model.document import Document
from six import string_types, iteritems
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil

class LotCreation(Document):
	def on_submit(self):
		default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
		abbr = frappe.db.get_value("Company",f"{default_company}","abbr")
		parent = "Lot Warehouse"
		create_parent_warehouse(parent,abbr)
		create_warehouse(self,parent,abbr)

	def make_material_request(self):

		'''Create Material Requests grouped by Sales Order and Material Request Type'''
		material_request_list = []
		material_request_map = {}

		for item in self.mr_items:
			item_doc = frappe.get_cached_doc('Item', item.item_code)

			material_request_type = item.material_request_type or item_doc.default_material_request_type

			# key for Sales Order:Material Request Type:Customer
			key = '{}:{}:{}'.format(item.sales_order, material_request_type, item_doc.customer or '')
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
			material_request.append("items", {
				"item_code": item.item_code,
				"qty": item.quantity,
				"schedule_date": schedule_date,
                # Todo : need to get the abbr of the company
				"warehouse": f'{self.name} - AT',
				"sales_order": item.sales_order,
				'lot_creation': self.name,
				'material_request_plan_item': item.name,
				"project": frappe.db.get_value("Sales Order", item.sales_order, "project") \
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
			material_request_list = ["""<a href="#Form/Material Request/{0}">{1}</a>""".format(m.name, m.name) \
				for m in material_request_list]
			msgprint(_("{0} created").format(comma_and(material_request_list)))
		else :
			msgprint(_("No material request created"))

@frappe.whitelist()
def get_ipd_item(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	doc['po_items'] = []
	po_items=[]
	item_production_detail=doc.get('item_production_detail')
	item_template=frappe.db.get_value("Item Production Detail",{'name': item_production_detail},"item")
	item_code=frappe.db.get_all("Item", fields=["item_code"], filters={"variant_of": item_template})
	for item in item_code:
		po_items.append({"item_code":item.get("item_code"),"bom_no":get_item_details(item.get("item_code")).get("bom_no")})
	return po_items
def create_parent_warehouse(name,abbr):
	if not frappe.db.exists("Warehouse",f'{name} - {abbr}'):
		frappe.get_doc({
			"doctype":"Warehouse",
			"warehouse_name": name,
			"is_group": 1,
			"parent_warehouse":f"All Warehouses - {abbr}"
			}).save()
def create_warehouse(self,parent,abbr):
	if not frappe.db.exists("Warehouse",f"{self.name} - {abbr}"):
		frappe.get_doc({
			"doctype":"Warehouse",
			"warehouse_name": self.name,
			"is_group": 0,
			"parent_warehouse":f"{parent} - {abbr}"
			}).save()
# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.model.document import Document
from six import string_types, iteritems
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
class LotCreation(Document):
	def on_submit(self):
		default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
		abbr = frappe.db.get_value("Company",f"{default_company}","abbr")
		parent = "Lot Warehouse"
		create_parent_warehouse(parent,abbr)
		create_warehouse(self,parent,abbr)
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
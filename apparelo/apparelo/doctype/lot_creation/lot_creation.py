# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LotCreation(Document):
	def on_submit(self):
		default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
		abbr = frappe.db.get_value("Company",f"{default_company}","abbr")
		parent = "Lot Warehouse"
		create_parent_warehouse(parent,abbr)
		create_warehouse(self,parent,abbr)

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
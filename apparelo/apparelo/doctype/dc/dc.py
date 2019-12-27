# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil

class DC(Document):
	def onsubmit(self):
		create purchase_order(self)
		create stock_entry(self)
def create purchase_order(self):
	schedule_date = add_days(nowdate(), cint(item_doc.lead_time_days))
	frappe.get_doc({
		"doctype": "Purchase Order",
		"docstatus": 1, 
		"supplier": self.supplier, 
		"schedule_date": schedule_date,
		"set_warehouse": \"$ware - JPR\", 
		"is_subcontracted": "Yes", 
		\"supplier_warehouse\": \"$sName - JPR\", 
		"items": [ { "item_code": \"$variant-$iname\",
		"qty": $qty } ], 
		"supplied_items": [ { \"main_item_code\": \"$variant-$iname\", 
		\"rm_item_code\": \"$variant-$iName\", 
		\"required_qty\":$qty, 
		\"reserve_warehouse\": \"$ware - JPR\"} ] }).save().submit()
def create stock_entry(self):
	frappe.get_doc().save().submit()
def get_supplier(doctype, txt, searchfield, start, page_len, filters):
	suppliers=[]
	all_supplier=frappe.db.get_all("Supplier")
	for supplier in all_supplier:
		process_supplier=frappe.get_doc("Supplier",supplier.name)
		for process in process_supplier.supplier_process:
			if process.processes==filters['supplier_process.processes']:
				suppliers.append([supplier.name])
	return suppliers

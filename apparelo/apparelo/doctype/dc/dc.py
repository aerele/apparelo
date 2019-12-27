# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
<<<<<<< HEAD
<<<<<<< HEAD
import frappe
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil
from apparelo.apparelo.doctype.lot_creation.lot_creation import create_parent_warehouse

class DC(Document):
	def on_submit(self):
		default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
		abbr = frappe.db.get_value("Company",f"{default_company}","abbr")
		parent= "Supplier Warehouse"
		create_parent_warehouse(parent,abbr)
		create_warehouse(self,parent,abbr)
		new_po=create_purchase_order(self,abbr)
		stock_entry_type="Material Receipt"
		po=""
		create_stock_entry(self,po,stock_entry_type,abbr)
		stock_entry_type="Send to Subcontractor"
		create_purchase_receipt(self,new_po,abbr)
		create_stock_entry(self,new_po,stock_entry_type,abbr)
def create_warehouse(self,parent,abbr):
	if not frappe.db.exists("Warehouse",f"{self.supplier} - {abbr}"):
		frappe.get_doc({
			"doctype":"Warehouse",
			"warehouse_name": self.supplier,
			"is_group": 0,
			"parent_warehouse":f"{parent} - {abbr}"
			}).save()
def create_purchase_order(self,abbr):
	dc_items=[]
	supplied_items=[]
	# schedule_date=None
	for item in self.items:
		# item_doc = frappe.get_cached_doc('Item', item.item_code)
		# schedule_date = add_days(nowdate(), cint(item_doc.lead_time_days))
		dc_items.append({ "item_code": item.item_code,"schedule_date": add_days(nowdate(), 7),"qty": item.weight})
		supplied_items.append({ "main_item_code": item.item_code, "rm_item_code": item.item_code, "required_qty":item.weight, "reserve_warehouse": f'{self.lot} - {abbr}'})
	po=frappe.get_doc({
		"doctype": "Purchase Order",
		"docstatus": 1, 
		"supplier": self.supplier, 
		"schedule_date": add_days(nowdate(), 7),
		"set_warehouse": f'{self.lot} - {abbr}', 
		"is_subcontracted": "Yes", 
		"supplier_warehouse": f'{self.supplier} - {abbr}', 
		"items": dc_items, 
		"supplied_items": supplied_items})
	po.save()
	return po
def create_purchase_receipt(self,po,abbr):
	item_list=[]
	for item in po.items:
		item_list.append({ "item_code": item.item_name, "qty": item.qty,"bom": item.bom,"schedule_date": add_days(nowdate(), 7) ,"warehouse": f'{self.lot} - {abbr}'})
	frappe.get_doc({ 
		"docstatus": 1, 
		"supplier": self.supplier, 
		"set_warehouse": f'{self.lot} - {abbr}', 
		"is_subcontracted": "Yes", 
		"supplier_warehouse": f'{self.supplier} - {abbr}', 
		"doctype": "Purchase Receipt", 
		"items": item_list }).save()
def create_stock_entry(self,po,stock_entry_type,abbr):
	item_list=[]
	for item in self.items:
		item_list.append({"allow_zero_valuation_rate": 1,"s_warehouse": f'{self.lot} - {abbr}',"t_warehouse": f'{self.supplier} - {abbr}',"item_code": item.item_code,"qty": item.weight })
	if po=="":
		frappe.get_doc({ 
			"docstatus": 1,
			"stock_entry_type": stock_entry_type,
			"doctype": "Stock Entry", 
			"items": item_list}).save()
	else:
		frappe.get_doc({ 
			"docstatus": 1,
			"stock_entry_type": stock_entry_type,
			"purchase_order": po.name,
			"doctype": "Stock Entry", 
			"items": item_list}).save()
def get_supplier(doctype, txt, searchfield, start, page_len, filters):
	suppliers=[]
	all_supplier=frappe.db.get_all("Supplier")
	for supplier in all_supplier:
		process_supplier=frappe.get_doc("Supplier",supplier.name)
		for process in process_supplier.supplier_process:
			if process.processes==filters['supplier_process.processes']:
				suppliers.append([supplier.name])
	return suppliers
def make_custom_fields(update=True):
	custom_fields={'Supplier': [
		{
	"fieldname": "supplier_process", 
	"fieldtype": "Table", 
	"label": "Supplier Process", 
	"options": "Supplier_Process", 
	"reqd": 1
	}
	]
	}
	create_custom_fields(custom_fields,ignore_validate = frappe.flags.in_patch, update=update)
=======
# import frappe
=======
import frappe
>>>>>>> 8848caf... Supplier filteration
from frappe.model.document import Document
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil

class DC(Document):
<<<<<<< HEAD
	pass
>>>>>>> 6e84224... DC doctype creation:
=======
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
>>>>>>> 8848caf... Supplier filteration

# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe ,json
from frappe import _,msgprint
from six import string_types, iteritems
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil
from apparelo.apparelo.doctype.lot_creation.lot_creation import create_parent_warehouse
from erpnext.stock.report.stock_balance.stock_balance import execute
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
		stock=create_stock_entry(self,po,stock_entry_type,abbr)
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Material Request/{0}">{1}</a>""".format(new_po.name, new_po.name))))
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Material Request/{0}">{1}</a>""".format(stock.name, stock.name))))
		# msgprint(_([new_po.name]))
		# msgprint(_([stock.name]))
		# stock_entry_type="Send to Subcontractor"
		# create_purchase_receipt(self,new_po,abbr)
		# create_stock_entry(self,new_po,stock_entry_type,abbr)
		pass
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
	for item_ in self.return_materials:
		dc_items.append({ "item_code": item_.item_code,"schedule_date": add_days(nowdate(), 7),"qty": item_.quantity})
	for item in self.items:
		supplied_items.append({ "main_item_code": item.item_code, "rm_item_code": item.item_code, "required_qty":item.quantity, "reserve_warehouse": f'{self.lot} - {abbr}'})
	po=frappe.get_doc({
		"doctype": "Purchase Order",
		"docstatus": 1, 
		"supplier": self.supplier,
		"dc":self.name,
		"lot":self.lot,
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
	for item in self.return_materials:
		item_list.append({"allow_zero_valuation_rate": 1,"s_warehouse": f'{self.lot} - {abbr}',"t_warehouse": f'{self.supplier} - {abbr}',"item_code": item.item_code,"qty": item.quantity })
	if po=="":
		se=frappe.get_doc({ 
			"docstatus": 1,
			"stock_entry_type": stock_entry_type,
			"doctype": "Stock Entry", 
			"items": item_list})
		se.save()
	else:
		se=frappe.get_doc({ 
			"docstatus": 1,
			"stock_entry_type": stock_entry_type,
			"purchase_order": po.name,
			"doctype": "Stock Entry", 
			"items": item_list})
		se.save()
	return se
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
	],
	'BOM': [
		{
	"fieldname": "process", 
	"fieldtype": "Link", 
	"label": "Process", 
	"options": "Multi Process"
		}
	],
	'Purchase Order': [
		{
	"fieldname": "dc", 
	"fieldtype": "Link", 
	"label": "DC", 
	"options": "DC"
		},
		{
	"fieldname": "lot", 
	"fieldtype": "Link", 
	"label": "Lot", 
	"options": "Lot Creation"
		}
	]
	}
	create_custom_fields(custom_fields,ignore_validate = frappe.flags.in_patch, update=update)
@frappe.whitelist()
def get_ipd_item(doc):
	default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
	abbr = frappe.db.get_value("Company",f"{default_company}","abbr")
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	doc['items'] = []
	items=[]
	lot=doc.get('lot')
	process=doc.get('process_1')
	process_index=''
	item_production_detail=frappe.db.get_value("Lot Creation",{'name': lot},"item_production_detail")
	ipd=frappe.db.get_value('IPD Item Mapping', {'item_production_details': item_production_detail}, 'name')
	ipd_item=frappe.get_doc('IPD Item Mapping',ipd)
	for item in ipd_item.item_mapping:
		if process=='Knitting':
			col, data = execute(filters=frappe._dict({'warehouse':f'{lot} - {abbr}',
							'from_date':frappe.utils.get_datetime('01-01-1970'),
							'to_date':frappe.utils.get_datetime(nowdate()),'item_code':item.input_item}))
			items.append({"item_code":item.input_item,"available_quantity":data[0]['bal_qty'],'uom':data[0]['stock_uom']})
		if process==item.process_1:
			if 'A' in item.ipd_process_index and item.input_index=='':
				process_index=item.ipd_process_index
				break
			else:
				process_index=item.input_index
				break
	input_indexs = process_index.split(',')	
	for item in ipd_item.item_mapping:
		for index in input_indexs:
			if str(item.ipd_process_index)==index:
				col, data = execute(filters=frappe._dict({'warehouse':f'{lot} - {abbr}',
							'from_date':frappe.utils.get_datetime('01-01-1970'),
							'to_date':frappe.utils.get_datetime(nowdate()),'item_code':item.item}))
				items.append({"item_code":item.item,"available_quantity":data[0]['bal_qty'],'uom':data[0]['stock_uom']})				
	return items
@frappe.whitelist()
def item_return(doc):
	process_bom=[]
	return_materials=[]
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	doc['return_materials'] = []
	items= doc.get('items')
	if not items:
		frappe.throw(_("Items are required to calculate return items"))
	lot=doc.get('lot')
	process=doc.get('process_1')
	# lot='test-lot'
	# process='Dyeing'
	ipd=frappe.get_doc("Lot Creation",lot)
	lot_ipd=ipd.item_production_detail
	bom=frappe.get_all("IPD BOM Mapping")
	for bom_ in bom:
		ipd_bom=frappe.get_doc("IPD BOM Mapping",bom_.name)
		if ipd_bom.item_production_details==lot_ipd:
			for bom_map in ipd_bom.bom_mapping:
				if bom_map.process_1==process:
					process_bom.append(bom_map.bom)
	total_bom=len(process_bom)
	for bom in process_bom:
		bom_=frappe.get_doc("BOM",bom)
		for item in bom_.items:
			for data in items:
				ordered_qunatity=data.get('quantity')
				per_item=ordered_qunatity/total_bom
				if data.get('item_code')==item.item_code:
					return_materials.append({"item_code":bom_.item,"uom":bom_.uom,"quantity":per_item/item.qty})
	return return_materials

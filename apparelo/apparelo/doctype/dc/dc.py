# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _, msgprint
from six import string_types, iteritems
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil
from erpnext.stock.report.stock_balance.stock_balance import execute
from apparelo.apparelo.doctype.item_production_detail.item_production_detail import process_based_qty
class DC(Document):
	def on_submit(self):
		default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
		abbr = frappe.db.get_value("Company",f"{default_company}","abbr")
		new_po=create_purchase_order(self,abbr)
		stock_entry_type="Material Receipt"
		po=""
		stock=create_stock_entry(self,po,stock_entry_type,abbr)
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Purchase Order/{0}">{1}</a>""".format(new_po.name, new_po.name))))
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Stock Entry/{0}">{1}</a>""".format(stock.name, stock.name))))

def create_purchase_order(self,abbr):
	dc_items=[]
	supplied_items=[]
	for item_ in self.return_materials:
		dc_items.append({ "item_code": item_.item_code,"schedule_date": add_days(nowdate(), 7),"qty": item_.quantity})
	for item in self.items:
		supplied_items.append({ "main_item_code": item.item_code, "rm_item_code": item.item_code, "required_qty":item.quantity, "reserve_warehouse":  f'{self.lot} - {self.location} - {abbr}'})
	po=frappe.get_doc({
		"doctype": "Purchase Order",
		"docstatus": 1,
		"supplier": self.supplier,
		"dc":self.name,
		"lot":self.lot,
		"schedule_date": add_days(nowdate(), 7),
		"set_warehouse": f'{self.lot} - {self.location} - {abbr}',
		"is_subcontracted": "Yes",
		"supplier_warehouse": f'{self.supplier} - {abbr}',
		"items": dc_items,
		"supplied_items": supplied_items})
	po.save()
	return po
def create_purchase_receipt(self,po,abbr):
	item_list=[]
	for item in po.items:
		item_list.append({ "item_code": item.item_name, "qty": item.qty,"bom": item.bom,"schedule_date": add_days(nowdate(), 7) ,"warehouse":  f'{self.lot} - {self.location} - {abbr}'})
	frappe.get_doc({ 
		"docstatus": 1, 
		"supplier": self.supplier, 
		"set_warehouse":  f'{self.lot} - {self.location} - {abbr}',
		"is_subcontracted": "Yes", 
		"supplier_warehouse": f'{self.supplier} - {abbr}', 
		"doctype": "Purchase Receipt", 
		"items": item_list }).save()
def create_stock_entry(self,po,stock_entry_type,abbr):
	item_list=[]
	for item in self.return_materials:
		item_list.append({"allow_zero_valuation_rate": 1,"s_warehouse":  f'{self.lot} - {self.location} - {abbr}',"t_warehouse": f'{self.supplier} - {abbr}',"item_code": item.item_code,"qty": item.quantity })
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
def make_item_fields(update=True):
	custom_fields={'Item': [
		{
	"fieldname": "print_code",
	"fieldtype": "Data",
	"label": "PF Item Code",
		}
	]}
	create_custom_fields(custom_fields,ignore_validate = frappe.flags.in_patch, update=update)
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
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))

	doc['items'] = []

	lot=doc.get('lot')
	if not frappe.get_doc('Lot Creation', lot).docstatus:
		frappe.throw(_(f'Lot {lot} is not yet submitted'))

	dc_process=doc.get('process_1')
	apparelo_process=frappe.get_doc("Apparelo Process",dc_process)
	location = doc.get('location')

	lot_ipd = frappe.db.get_value('Lot Creation', {'name': lot}, 'item_production_detail')
	ipd_bom_mapping = frappe.db.get_value("IPD BOM Mapping", {'item_production_details': lot_ipd})
	boms = frappe.get_doc('IPD BOM Mapping', ipd_bom_mapping).get_process_boms(dc_process)

	items_to_be_sent = frappe.get_list("BOM Item", filters={'parent': ['in',boms]}, group_by='item_code', fields='item_code')

	from erpnext.stock.dashboard import item_dashboard
	dc_warehouse = frappe.db.get_value('Warehouse', {'warehouse_name': f'{lot}-{location}'}, 'name')
	for item in items_to_be_sent:
		data = item_dashboard.get_data(item_code = item.item_code, warehouse = dc_warehouse)
		if len(data):
			item['available_quantity'] = data[0]['actual_qty']
			item_detail = frappe.get_doc('Item', item.item_code)
			item['primary_uom'] = item_detail.stock_uom
			item['secondary_uom'] = apparelo_process.in_secondary_uom
			item['pf_item_code'] = item_detail.print_code
	return items_to_be_sent


@frappe.whitelist()
def item_return(doc):
	index=[]
	process_list=set()
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))

	doc['return_materials'] = []

	items = doc.get('items')
	if not items:
		frappe.throw(_("Items are required to calculate return items"))

	lot = doc.get('lot')
	dc_process = doc.get('process_1')
	apparelo_process=frappe.get_doc("Apparelo Process",dc_process)
	lot_ipd = frappe.db.get_value('Lot Creation', {'name': lot}, 'item_production_detail')
	lot_ipd_doc=frappe.get_doc("Item Production Detail",lot_ipd)
	for process in lot_ipd_doc.processes:
		if process.process_name==dc_process:
			index.append(process.idx)
	for process in lot_ipd_doc.processes:
		for idx in index:
			if process.input_index:
				if str(idx) == process.input_index:
					process_list.add(process.process_name)
	additional_item_list,expected_items_in_return=process_based_qty(process=list(process_list),lot=lot)
	ipd_item_map = frappe.get_doc("IPD Item Mapping",{'item_production_details': lot_ipd})
	for item in expected_items_in_return:
		for ipd_item in ipd_item_map.item_mapping:
			if ipd_item.item == item['item_code']:
				item_detail = frappe.get_doc('Item', item['item_code'])
				item['description'] = ipd_item.description
				item['secondary_uom'] = apparelo_process.out_secondary_uom
				item['pf_item_code'] = item_detail.print_code
	return expected_items_in_return
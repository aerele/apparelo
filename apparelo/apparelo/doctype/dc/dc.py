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
from erpnext.buying.doctype.purchase_order.purchase_order import make_rm_stock_entry
class DC(Document):
	def on_submit(self):
		new_po=self.create_purchase_order()
		rm_items = []
		for item in new_po.supplied_items:
			item_list = {}
			item_list['name'] = item.name
			item_list['item_code'] = item.main_item_code
			item_list['rm_item_code'] = item.rm_item_code
			item_list['item_name'] = item.rm_item_code
			item_list['qty'] = item.required_qty
			item_list['warehouse'] = item.reserve_warehouse
			item_list['rate'] = item.rate
			item_list['amount'] = item.amount
			item_list['stock_uom'] = item.stock_uom
			rm_items.append(item_list)
		stock_dict = make_rm_stock_entry(new_po.name, json.dumps(rm_items))
		stock_entry = frappe.get_doc(stock_dict)
		stock_entry.save()
		stock_entry.submit()

		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Purchase Order/{0}">{1}</a>""".format(new_po.name, new_po.name))))
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Stock Entry/{0}">{1}</a>""".format(stock_entry.name, stock_entry.name))))

	def create_purchase_order(self):
		dc_items=[]
		supplied_items=[]
		lot_warehouse= frappe.db.get_value("Warehouse", {'location': self.location,'lot': self.lot,'warehouse_type': "Actual"},'name')
		supplier_warehouse=frappe.db.get_value("Warehouse", {'supplier': self.supplier},'name')
		for item_ in self.return_materials:
			dc_items.append({ "item_code": item_.item_code,"schedule_date": add_days(nowdate(), 7),"qty": item_.qty})
		for item in self.items:
			supplied_items.append({ "main_item_code": item.item_code, "rm_item_code": item.item_code, "required_qty":item.quantity, "reserve_warehouse": lot_warehouse})
		po=frappe.get_doc({
			"doctype": "Purchase Order",
			"supplier": self.supplier,
			"dc":self.name,
			"lot":self.lot,
			"schedule_date": add_days(nowdate(), 7),
			"set_warehouse": lot_warehouse,
			"set_reserve_warehouse": lot_warehouse,
			"is_subcontracted": "Yes",
			"supplier_warehouse": supplier_warehouse,
			"items": dc_items,
			"supplied_items": supplied_items})
		po.save()
		po.submit()
		return po

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
	dc_warehouse = frappe.db.get_value("Warehouse", {'location': location,'lot': lot,'warehouse_type':'Actual'},'name')
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
				item['additional_parameters'] = get_additional_params(lot_ipd_doc.processes, ipd_item.ipd_process_index)
				item['secondary_uom'] = apparelo_process.out_secondary_uom
				item['pf_item_code'] = item_detail.print_code
	return expected_items_in_return

def get_additional_params(ipd_processes, ipd_process_index):
	ipd_process_array_index = int(ipd_process_index)-1
	if ipd_processes[ipd_process_array_index].idx == int(ipd_process_index):
		process_name = ipd_processes[ipd_process_array_index].process_name
		process_record = ipd_processes[ipd_process_array_index].process_record
		process_doc = frappe.get_doc(process_name, process_record)
		if process_doc.additional_information:
			additional_parameters_string = ''
			for info in process_doc.additional_information:
				additional_parameters_string += f'{info.parameter} : {info.value}\n'
			return additional_parameters_string
		else:
			return None
	else:
		frappe.throw(_("Unexpected error in getting additional params. IPD processes list was probably not sorted during fetch."))

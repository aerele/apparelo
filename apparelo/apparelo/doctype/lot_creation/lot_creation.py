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
from apparelo.apparelo.doctype.dc.dc import get_receivable_list_values
from erpnext.manufacturing.doctype.production_plan.production_plan import get_items_for_material_requests
from frappe.utils import today
from apparelo.apparelo.utils.item_utils import get_attr_dict
from numpy import prod


class LotCreation(Document):
	def on_submit(self):
		create_parent_warehouse(self)
		create_warehouse(self)

	def make_material_request(self):
		'''Create Material Requests grouped by Sales Order and Material Request Type'''
		material_request_list = []
		material_request_map = {}

		for item in self.mr_items:
			item_doc = frappe.get_cached_doc('Item', item.item_code)

			material_request_type = item_doc.default_material_request_type
			# key for Sales Order:Material Request Type:Customer
			key = '{}:{}:{}'.format(
					item.sales_order, material_request_type, item_doc.customer or '')
			if material_request_type == 'Purchase':
				if not key in material_request_map:
					# make a new MR for the combination
					material_request_map[key] = frappe.new_doc("Material Request")
					material_request = material_request_map[key]
					material_request.update({
						"lot": self.name,
						"transaction_date": nowdate(),
						"status": "Draft",
						"company": frappe.db.get_single_value('Global Defaults', 'default_company'),
						"requested_by": frappe.session.user,
						"material_request_type": material_request_type,
						"customer": item_doc.customer or ""
					})
					material_request_list.append(material_request)
				else:
					material_request = material_request_map[key]

			else:
				if not key in material_request_map:
					# make a new MR for the combination
					material_request_map[key] = frappe.new_doc("Material Request")
					material_request = material_request_map[key]
					material_request.update({
						"lot": self.name,
						"transaction_date": nowdate(),
						"status": "Draft",
						"company": frappe.db.get_single_value('Global Defaults', 'default_company'),
						"requested_by": frappe.session.user,
						"material_request_type": material_request_type,
						"customer": item_doc.customer or ''
					})
					material_request_list.append(material_request)
				else:
					material_request = material_request_map[key]

			# add item
			material_request.append("items", {
				"item_code": item.item_code,
				"qty": item.quantity,
				"schedule_date": item.req_by_date,
				"sales_order": item.sales_order,
				"lot_creation": self.name,
				"material_request_plan_item": item.name,
				"project": frappe.db.get_value("Sales Order", item.sales_order, "project")
					if item.sales_order else None
			})

		for material_request in material_request_list:
			# submit
			material_request.flags.ignore_permissions = 1
			material_request.run_method("set_missing_values")

			# if self.get('submit_material_request'):
			# 	material_request.submit()
			# else:
			material_request.save()

		frappe.flags.mute_messages = False

		if material_request_list:
			material_request_list = ["""<a href="#Form/Material Request/{0}">{1}</a>""".format(m.name, m.name)
				for m in material_request_list]
			msgprint(_("{0} created").format(comma_and(material_request_list)))
		else:
			msgprint(_("No material request created"))

default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
abbr = frappe.db.get_value("Company", f"{default_company}", "abbr")

@frappe.whitelist()
def get_base_materials(doc, ignore_existing_ordered_qty=None):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	if frappe.db.get_value('Item Production Detail', doc['item_production_detail'], 'is_combined_packing'):
		for idx, po_item in enumerate(doc.po_items):
			doc.po_items[idx]['include_exploded_items'] = 0
	
	doc['ignore_existing_ordered_qty'] = True
	doc['include_subcontracted_items'] = True
	mr_items = get_items_for_material_requests(doc)
	for item in mr_items:
		if item['uom'] == 'Nos':
			if round(item['quantity'] + (item['quantity'] * float(doc.get('percentage')))/100) < (item['quantity'] + (item['quantity'] * float(doc.get('percentage')))/100):
				item['quantity']=round(item['quantity'] + (item['quantity'] * float(doc.get('percentage')))/100) + 1
			else:
				item['quantity']=round(item['quantity'] +(item['quantity'] * float(doc.get('percentage')))/100)
		else:
			item['quantity']=item['quantity'] +(item['quantity'] * float(doc.get('percentage')))/100

		item['req_by_date'] = today()
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
	ipd_sizes =[]
	for _size in frappe.get_doc('Item Production Detail',item_production_detail).size:
		ipd_sizes.append(_size.size)
	item_code=frappe.db.get_all("Item", fields = ["item_code"], filters = {
	                            "variant_of": item_template})
	for _size in ipd_sizes:
		for item in item_code:
			item_doc=frappe.get_doc("Item",item.get('item_code'))
			item_attr = get_attr_dict(item_doc.attributes)
			if _size==item_attr['Apparelo Size'][0]:
				po_items.append({"item_code": item.get("item_code"), "bom_no": get_item_details(item.get("item_code")).get("bom_no")})
				break
	return po_items

def create_parent_warehouse(self):
	lot_warehouse=frappe.db.get_value("Warehouse", {'warehouse_name': self.name,'parent_warehouse': f"Lot Warehouse - {abbr}"},'name')
	if not lot_warehouse:
		frappe.get_doc({
			"doctype": "Warehouse",
			"warehouse_name": self.name,
			"is_group": 1,
			"parent_warehouse": f"Lot Warehouse - {abbr}"
			}).save()

def create_warehouse(self):
	for location in self.location:
		lot_warehouse= frappe.db.get_value("Warehouse", {'location': location.location,'lot': self.name,'warehouse_type': 'Actual'},'name')
		mistake_warehouse= frappe.db.get_value("Warehouse", {'location': location.location,'lot': self.name,'warehouse_type':'Mistake'},'name')
		if not lot_warehouse:
			frappe.get_doc({
				"doctype": "Warehouse",
				"location": location.location,
				"lot": self.name,
				"warehouse_type":'Actual',
				"warehouse_name": f"{self.name}-{location.location}",
				"is_group": 0,
				"parent_warehouse": f"{self.name} - {abbr}"
				}).save()
		if not mistake_warehouse:
			frappe.get_doc({
				"doctype": "Warehouse",
				"location": location.location,
				"lot": self.name,
				"warehouse_type":'Mistake',
				"warehouse_name": f"{self.name}-{location.location} Mistake",
				"is_group": 0,
				"parent_warehouse": f"{self.name} - {abbr}"
				}).save()

@frappe.whitelist()
def cloth_qty(doc):
	if isinstance(doc, string_types):
		doc=frappe._dict(json.loads(doc))
	html_head = '<th>Dia/Colour</th>'
	html = ''
	bom_qty = []
	process = []
	colour_list = set()
	dia_list = []
	yarn_list=[]
	# get bom and planned quantity
	for item in doc.po_items:
		bom_qty.append({item['bom_no']:item['planned_qty']})

	ipd = frappe.get_doc('Item Production Detail',doc.item_production_detail)
	colour_count = len(ipd.colour)
	final_process = frappe.db.get_value("Item Production Detail",{'name':doc.item_production_detail}, 'final_process')
	process_record = frappe.db.get_value("Item Production Detail Process",{'parent': doc.item_production_detail,'process_name':final_process},'process_record')
	input_qty = frappe.db.get_value("Packing",process_record,'input_qty')
	# get yarn, dia and end process list
	knit_idx = []
	for ipd_process in ipd.processes:
		if ipd_process.process_name == 'Knitting':
			knit_idx.append(str(ipd_process.idx))
			dia_list = []
			knitted_colour = []
			for knitting_dia in frappe.get_doc('Knitting',ipd_process.process_record).dia:
				dia_list.append(knitting_dia.dia)
			process_name =  frappe.get_list("Item Production Detail Process", filters={'parent': ['in',doc.item_production_detail],'input_index':ipd_process.idx}, fields=['process_name','process_record'])
			if not process_name:
				process_name =  frappe.get_list("Item Production Detail Process", filters={'parent': ['in',doc.item_production_detail],'input_index':','.join(knit_idx)}, fields=['process_name','process_record'])
				if process_name:
					knit_idx = []
			if process_name:
				if process_name[0]['process_name'] == 'Bleaching':
					table = frappe.get_doc(process_name[0]['process_name'],process_name[0]['process_record']).types
				else:
					table = frappe.get_doc(process_name[0]['process_name'],process_name[0]['process_record']).colours
			for colth_colour in table:
				knitted_colour.append(colth_colour.colour)
				colour_list.add(colth_colour.colour)
			yarn_list.append({'yarn': ipd_process.input_item, 'index': ipd_process.idx, 'dia': dia_list})
		elif ipd_process.process_name == 'Compacting' or ipd_process.process_name == 'Steaming':
			process.append(ipd_process.process_name)
	process = list(set(process))
	colour_list = list(colour_list)
	# get colour list
	for colour in colour_list:
		html_head += f'<th>{colour}</th>'
	html_head += '<th>Total</th>'

	final_item_list = []
	if doc['item_production_detail']:
		ipd_bom_mapping = frappe.db.get_value("IPD BOM Mapping", {'item_production_details': doc['item_production_detail']})
		boms = frappe.get_doc('IPD BOM Mapping', ipd_bom_mapping).get_process_boms('Dyeing')
		boms.extend(frappe.get_doc('IPD BOM Mapping', ipd_bom_mapping).get_process_boms('Bleaching'))

		items_to_be_received = frappe.get_list('BOM', filters={'name': ['in', boms]}, group_by='item', fields='item')
		receivable_list = {}
		for item_to_be_received in items_to_be_received:
			receivable_list[item_to_be_received['item']] = 0

		receivable_list = get_receivable_list_values(doc.po_items, receivable_list)

		for item_to_be_received in items_to_be_received:
			item = frappe.get_doc('Item', item_to_be_received['item'])
			item_list = {}
			item_list['item_code'] = item_to_be_received['item']
			item_list['qty'] = flt(receivable_list[item_to_be_received['item']] + (receivable_list[item_to_be_received['item']] * (flt(doc.percentage)/100)), 3)
			item_list['uom'] = item.stock_uom
			final_item_list.append(item_list)
	combined_input_idx = []
	for data in yarn_list:
		html_body = ''
		dia_qty_list =[]
		combined_input_idx.append(str(data['index']))
		ipd_item_mapping_name = frappe.db.get_value('IPD Item Mapping',{'item_production_details':doc.item_production_detail},'name')
		ipd_items = frappe.get_list("Item Mapping", filters={'parent': ['in',ipd_item_mapping_name],'input_index':data['index']}, fields='item')
		if not ipd_items:
			ipd_items = frappe.get_list("Item Mapping", filters={'parent': ['in',ipd_item_mapping_name],'input_index':','.join(combined_input_idx)}, fields='item')
			if ipd_items:
				combined_input_idx = []
		ipd_item_list = []
		for item in ipd_items:
			ipd_item_list.append(item['item'])
		for dia in data['dia']:
			dia_list = [0]*(len(colour_list)+2)
			dia_list[0] = dia
			dia_total = 0
			for colour in colour_list:
				for item in final_item_list:
					item_doc = frappe.get_doc("Item",item['item_code'])
					item_attr = get_attr_dict(item_doc.attributes)
					if (colour==item_attr['Apparelo Colour'][0]) and (dia==item_attr['Dia'][0]) and (item['item_code'] in ipd_item_list):
						if input_qty < colour_count and item['qty']:
							combination_count = find_combination(colour_count, input_qty)
							qty = round(item['qty']/combination_count,3)
							dia_list[colour_list.index(colour)+1] = qty
							dia_total += qty
						else:
							dia_list[colour_list.index(colour)+1] = item['qty']
							dia_total += item['qty']
						if 'FOLD' in item['item_code']:
							dia_list[0] = f'{dia} (FOLD)'
						break
			dia_list[len(colour_list)+1] = round(dia_total,3)
			dia_qty_list.append(dia_list)
		for lists in dia_qty_list:
			for value in lists:
				html_body += f'<td>{value}</td>'
			html_body = f'<tr>{html_body}</tr>'
		html += f'<table class="table table-bordered"><tbody><tr>{data["yarn"]}</tr><tr>{html_head}</tr>{html_body}</tbody></table>'
	return html

@frappe.whitelist()
def create_new_warehouse(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))

	for location in doc.new_location:
		lot_warehouse= frappe.db.get_value("Warehouse", {'location': location['location'],'lot': doc.name,'warehouse_type': 'Actual'},'name')
		mistake_warehouse= frappe.db.get_value("Warehouse", {'location': location['location'],'lot': doc.name,'warehouse_type':'Mistake'},'name')
		if not lot_warehouse:
			frappe.get_doc({
				"doctype": "Warehouse",
				"location": location['location'],
				"lot": doc.name,
				"warehouse_type":'Actual',
				"warehouse_name": f"{doc.name}-{location['location']}",
				"is_group": 0,
				"parent_warehouse": f"{doc.name} - {abbr}"
				}).save()
		if not mistake_warehouse:
			frappe.get_doc({
				"doctype": "Warehouse",
				"location": location['location'],
				"lot": doc.name,
				"warehouse_type":'Mistake',
				"warehouse_name": f"{doc.name}-{location['location']} Mistake",
				"is_group": 0,
				"parent_warehouse": f"{doc.name} - {abbr}"
				}).save()

def find_combination(n, r):
	numerator = range(n, max(n-r,r),-1)
	denominator = range(1, min(n-r,r) +1,1)
	return int(prod(numerator)/prod(denominator))


# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from frappe import _,msgprint
from frappe.model.document import Document
from six import string_types, iteritems
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil
from apparelo.apparelo.utils.item_utils import get_item_attribute_set
import itertools
from apparelo.apparelo.utils.utils import generate_printable_list, generate_html_from_list, generate_total_row_and_column
from apparelo.apparelo.doctype.dc.dc import get_grouping_params


class GRN(Document):
	def validate(self):
		self.set_po()
		printable_list_received = generate_printable_list(self.return_materials, self.get_grouping_params(),field='received_qty')
		printable_list_received[0]['section_title'] = 'Received Return Items'
		generate_total_row_and_column(printable_list_received)

		# Check for rejected quantity
		rejected_qty_items = [item for item in self.return_materials if vars(item)['rejected_qty']!=0]
		if rejected_qty_items:
			printable_list_rejected = generate_printable_list(rejected_qty_items, self.get_grouping_params(),field='rejected_qty')
			printable_list_rejected[0]['section_title'] = 'Rejected Return Items'
			generate_total_row_and_column(printable_list_rejected)
			printable_list_received+=printable_list_rejected
		self.grn_cloth_quantity = generate_html_from_list(printable_list_received)
	def on_submit(self):
		pr=self.create_purchase_receipt()
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Purchase Receipt/{0}">{1}</a>""".format(pr.name, pr.name))))
	
	def on_cancel(self):
		self.db_set("docstatus",2)
		msgprint(_("{0} cancelled").format(comma_and("""<a href="#Form/GRN/{0}">{1}</a>""".format(self.name, self.name))))
	
	def create_purchase_receipt(self):
		item_list=[]
		lot_warehouse= frappe.db.get_value("Warehouse", {'location': self.location,'lot': self.lot,'warehouse_type':'Actual'},'name')
		rejected_warehouse= frappe.db.get_value("Warehouse", {'location': self.location,'lot': self.lot,'warehouse_type':'Mistake'},'name')
		po_doc=frappe.get_doc("Purchase Order",self.po)
		for item in self.return_materials:
			item_list.append({"item_code": item.item_code, "received_qty": item.received_qty, "qty": item.received_qty - item.rejected_qty, "uom": item.uom, "stock_uom": item.uom, "rejected_qty": item.rejected_qty, "schedule_date": add_days(nowdate(), 7), "warehouse": lot_warehouse, "purchase_order": self.po})
		pr=frappe.get_doc({
			"supplier": self.supplier,
			"rejected_warehouse": rejected_warehouse,
			"set_warehouse": lot_warehouse,
			"is_subcontracted": po_doc.is_subcontracted,
			"supplier_warehouse": po_doc.supplier_warehouse,
			"doctype": "Purchase Receipt",
			"grn": self.name,
			"items": item_list })
		pr.save()
		pr.submit()
		return pr
	def set_po(self):
		if self.against_type == 'Purchase Order':
			self.po = self.against_document
		else:
			dc_doc = frappe.get_doc("DC", self.against_document)
			self.po = frappe.db.get_value("Purchase Order", {'dc':self.against_document}, 'name')

	def get_grouping_params(self):
		if self.against_type=='Purchase Order':
			return get_grouping_params('Raw Material')

		if self.against_type=="DC":
			process = frappe.db.get_value('DC',{'name': self.against_document},'process_1')
			return get_grouping_params(process)

def get_type(doctype, txt, searchfield, start, page_len, filters):
	if filters['type']=='DC':
		DC = [[dc['name']] for dc in frappe.get_list("DC", filters={'supplier': ['in',filters['supplier']],'lot':['in',filters['lot']]}, fields=["name"])]
		return DC
	else:
		PO = [[po['name']] for po in frappe.get_list("Purchase Order", filters={'supplier': ['in',filters['supplier']],'lot':['in',filters['lot']]}, fields=["name"])]
		return PO
def get_Lot(doctype, txt, searchfield, start, page_len, filters):
	lot_list = []
	for lot in frappe.get_list("Purchase Order", fields=["lot"]):
		if not lot['lot'] in lot_list:
			lot_list.append([lot['lot']])
	return lot_list
def get_supplier(doctype, txt, searchfield, start, page_len, filters):
	supplier_list = []
	for supplier in frappe.get_list("Purchase Order", fields=["supplier"]):
		if not supplier['supplier'] in supplier_list:
			supplier_list.append([supplier['supplier']])
	return supplier_list
@frappe.whitelist()
def get_items(doc):
	return_materials=[]
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	doc['return_materials'] = []
	doc_=doc.get("against_document")
	dc_process=None
	apparelo_process=None
	if doc.get("against_type")=="DC":
		dc_doc = frappe.get_doc("DC",doc_)
		dc_process=dc_doc.process_1
		doc_ = frappe.db.get_value("Purchase Order",{'dc':doc_},'name')
	PO=frappe.get_doc("Purchase Order",doc_)
	if dc_process:
		apparelo_process=frappe.get_doc("Apparelo Process",dc_process)
	pr_list = frappe.get_list(
		"Purchase Receipt Item",
		filters={'purchase_order': ['in', doc_]},
		fields=['parent'], group_by='parent'
		)
	if pr_list:
		pr_names = [pr["parent"] for pr in pr_list]
		pr_items = frappe.get_list("Purchase Receipt", filters={'name': ['in',pr_names]}, fields=["`tabPurchase Receipt Item`.item_code","`tabPurchase Receipt Item`.received_qty"]) 
		for key, group in itertools.groupby(pr_items, key=lambda x: (x['item_code'])):
			total_received_qty = 0 
			for item in group:
				total_received_qty+=item['received_qty']
			for item in PO.items:
				if item.item_code == key:
					item.qty-=total_received_qty
	for item in PO.items:
		return_material = {}
		item_detail = frappe.get_doc('Item', item.item_code)
		for attr in item_detail.attributes:
			if attr.attribute == "Dia":
				return_material['Dia'] = attr.attribute_value
			if attr.attribute == "Apparelo Colour":
				return_material['Apparelo Colour'] = attr.attribute_value
			if attr.attribute == "Apparelo Size":
				return_material['Apparelo Size'] = attr.attribute_value
		if apparelo_process:
			return_material.update({"item_code":item.item_code,"uom":item.uom,"qty":item.qty,"pf_item_code":item_detail.print_code,"secondary_uom":apparelo_process.in_secondary_uom})
			return_materials.append(return_material)
		else:
			return_material.update({"item_code":item.item_code,"uom":item.uom,"qty":item.qty,"pf_item_code":item_detail.print_code,"secondary_uom":item.uom})
			return_materials.append(return_material)
	if 'Dia' in return_materials[0]:
		if 'Apparelo Colour' in return_materials[0]:
			return_materials = sorted(sorted(return_materials, key = lambda i: i['Dia']), key = lambda i: i['Apparelo Colour'])
		else:
			return_materials = sorted(return_materials, key = lambda i: i['Dia'])
	if 'Apparelo Size' in return_materials[0]:
		return_materials = sorted(return_materials, key = lambda i: i['Apparelo Size'])
	return return_materials

@frappe.whitelist()
def divide_total_quantity(doc):
	return_materials = []
	total_expected_qty = 0
	matching_item_list = []
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	attribute = doc.get('attribute')
	attribute_value = doc.get('attribute_value')
	total_received_qty = doc.get('total_quantity_received')
	if total_received_qty:
		for return_material in doc['return_materials']:
			item_doc = frappe.get_doc("Item",return_material['item_code'])
			attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes,[item_doc])))
			if attribute_set[attribute][0] == attribute_value:
				total_expected_qty += return_material['qty']
				matching_item_list.append(return_material['item_code'])
		for return_item in doc['return_materials']:
			if return_item['item_code'] in matching_item_list:
				if total_received_qty>total_expected_qty:
					remaining_qty = total_received_qty - total_expected_qty
					return_item['received_qty'] = return_item['qty'] + (remaining_qty/total_expected_qty)*return_item['qty']
				else:
					return_item['received_qty'] = (total_received_qty/total_expected_qty)*return_item['qty']
				return_materials.append({"item_code":return_item['item_code'],"uom":return_item['uom'],"qty":return_item['qty'],"pf_item_code":return_item['pf_item_code'],"secondary_uom":return_item['secondary_uom'],"received_qty":return_item['received_qty']})
			else:
				if 'received_qty' in return_item:
					return_materials.append({"item_code":return_item['item_code'],"uom":return_item['uom'],"qty":return_item['qty'],"pf_item_code":return_item['pf_item_code'],"secondary_uom":return_item['secondary_uom'],"received_qty":return_item['received_qty']})
				else:
					return_materials.append({"item_code":return_item['item_code'],"uom":return_item['uom'],"qty":return_item['qty'],"pf_item_code":return_item['pf_item_code'],"secondary_uom":return_item['secondary_uom']})
	return return_materials

@frappe.whitelist()
def get_attribute_value(attribute):
	attribute_value_list = []
	attr_doc = frappe.get_doc("Item Attribute",attribute)
	for attr in attr_doc.item_attribute_values:
		attribute_value_list.append([attr.attribute_value])
	return attribute_value_list

@frappe.whitelist()
def duplicate_values(doc):
	grn_items = []
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	for item in doc.get('return_materials'):
		field_dict = {'Received Qty':'received_qty','Rejected Qty':'rejected_qty','Expected Qty':'qty'}
		if doc.from_field in field_dict and doc.to_field in field_dict:
			if 'secondary_qty' in item:
				item_dict = {"pf_item_code":item['pf_item_code'],"item_code":item['item_code'],field_dict[doc.from_field]:item[field_dict[doc.from_field]],field_dict[doc.to_field]:item[field_dict[doc.from_field]],"qty":item['qty'],"uom":item['uom'],"secondary_qty":item["secondary_qty"],"secondary_uom":item['secondary_uom']}
			else:
				item_dict = {"pf_item_code":item['pf_item_code'],"item_code":item['item_code'],field_dict[doc.from_field]:item[field_dict[doc.from_field]],field_dict[doc.to_field]:item[field_dict[doc.from_field]],"qty":item['qty'],"uom":item['uom'],"secondary_uom":item['secondary_uom']}	
		field_dict.pop(doc.from_field)
		field_dict.pop(doc.to_field)
		if list(field_dict.values())[0] in item:
			item_dict[list(field_dict.values())[0]]	= item[list(field_dict.values())[0]]
		grn_items.append(item_dict)
	return grn_items

@frappe.whitelist()
def delete_unavailable_return_items(doc):
	available_return_items = []
	if isinstance(doc, string_types):
    		doc = frappe._dict(json.loads(doc))
	for item in doc.get('return_materials'):
		item_dict={}
		if 'received_qty' in item:
			if 'rejected_qty' in item:
				if 'secondary_qty' in item:
					item_dict = {"pf_item_code":item['pf_item_code'],"item_code":item['item_code'],"qty":item['qty'],"received_qty":item['received_qty'],"rejected_qty":item['rejected_qty'],"uom":item['uom'],"secondary_qty":item['secondary_qty'],"secondary_uom":item['secondary_uom']}
				else:
					item_dict = {"pf_item_code":item['pf_item_code'],"item_code":item['item_code'],"qty":item['qty'],"received_qty":item['received_qty'],"rejected_qty":item['rejected_qty'],"uom":item['uom'],"secondary_uom":item['secondary_uom']}
			else:
				if 'secondary_qty' in item:
					item_dict = {"pf_item_code":item['pf_item_code'],"item_code":item['item_code'],"qty":item['qty'],"received_qty":item['received_qty'],"uom":item['uom'],"secondary_qty":item['secondary_qty'],"secondary_uom":item['secondary_uom']}
				else:
					item_dict = {"pf_item_code":item['pf_item_code'],"item_code":item['item_code'],"qty":item['qty'],"received_qty":item['received_qty'],"uom":item['uom'],"secondary_uom":item['secondary_uom']}

		if item_dict:
			available_return_items.append(item_dict)
	return available_return_items
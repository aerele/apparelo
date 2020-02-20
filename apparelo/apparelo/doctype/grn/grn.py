# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from frappe import _,msgprint
from frappe.model.document import Document
from six import string_types, iteritems
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil

class GRN(Document):
	def validate(self):
		get_po(self)
	def on_submit(self):
		default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
		abbr = frappe.db.get_value("Company",f"{default_company}","abbr")
		pr=create_purchase_receipt(self,abbr)
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Purchase Receipt/{0}">{1}</a>""".format(pr.name, pr.name))))
def create_purchase_receipt(self,abbr):
	item_list=[]
	PO_=frappe.get_doc("Purchase Order",self.po)
	for item in PO_.items:
		item_list.append({"item_code": item.item_name, "qty": item.qty, "bom": item.bom, "schedule_date": add_days(nowdate(), 7), "warehouse": f'{self.lot}-{self.location} - {abbr}', "purchase_order": self.po})
	pr = frappe.get_doc({
        "grn": self.name,
		"supplier": self.supplier, 
		"set_warehouse": f'{self.lot}-{self.location} - {abbr}', 
		"is_subcontracted": "Yes", 
		"supplier_warehouse": f'{self.supplier} - {abbr}', 
		"doctype": "Purchase Receipt", 
		"items": item_list })
	pr.save()
	pr.submit()
	return pr

def get_type(doctype, txt, searchfield, start, page_len, filters):
	if filters['type']=='DC':
		DC=[]
		all_dc=frappe.db.get_all("DC")
		for dc in all_dc:
			dc_=frappe.get_doc("DC",dc.name)
			if dc_.supplier == filters['supplier']:
				if dc_.lot == filters['lot']:
					DC.append([dc_.name])
		return DC
	else:
		PO=[]
		all_po=frappe.db.get_all("Purchase Order")
		for po in all_po:
			po_=frappe.get_doc("Purchase Order",po.name)
			if po_.supplier == filters['supplier']:
				if po_.lot == filters['lot']:
					PO.append([po_.name])
		return PO
def get_Lot(doctype, txt, searchfield, start, page_len, filters):
	Lot=set()
	lot=[]
	all_po=frappe.db.get_all("Purchase Order")
	for po in all_po:
		po_=frappe.get_doc("Purchase Order",po.name)
		Lot.add(po_.lot)
	for lot_ in Lot:
		lot.append([lot_])
	return lot
def get_supplier(doctype, txt, searchfield, start, page_len, filters):
	supplier=[]
	all_po=frappe.db.get_all("Purchase Order")
	for po in all_po:
		po_=frappe.get_doc("Purchase Order",po.name)
		supplier.append([po_.supplier])
	return supplier
@frappe.whitelist()
def get_items(doc):
	return_materials=[]
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	doc['return_materials'] = []
	doc_=doc.get("against_document")
	if doc_.startswith("D"):
		all_po=frappe.db.get_all("Purchase Order")
		for po in all_po:
			po_=frappe.get_doc("Purchase Order",po.name)
			if po_.dc==doc_:
				doc_=po_.name
	PO=frappe.get_doc("Purchase Order",doc_)
	for item in PO.items:
		return_materials.append({"item_code":item.item_code,"uom":item.uom,"quantity":item.qty})
	return return_materials
def get_po(self):
	doc_=self.against_document
	if doc_.startswith("D"):
		all_po=frappe.db.get_all("Purchase Order")
		for po in all_po:
			po_=frappe.get_doc("Purchase Order",po.name)
			if po_.dc==doc_:
				doc_=po_.name
	PO=frappe.get_doc("Purchase Order",doc_)
	self.po=PO.name
	return PO.name

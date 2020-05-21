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
		self.po=None
		self.get_po()
	def on_submit(self):
		pr=self.create_purchase_receipt()
		msgprint(_("{0} created").format(comma_and("""<a href="#Form/Purchase Receipt/{0}">{1}</a>""".format(pr.name, pr.name))))
	def create_purchase_receipt(self):
		item_list=[]
		lot_warehouse= frappe.db.get_value("Warehouse", {'location': self.location,'lot': self.lot,'warehouse_type':'Actual'},'name')
		rejected_warehouse= frappe.db.get_value("Warehouse", {'location': self.location,'lot': self.lot,'warehouse_type':'Mistake'},'name')
		po_doc=frappe.get_doc("Purchase Order",self.po)
		for item in self.return_materials:
			item_list.append({"item_code": item.item_code, "received_qty":item.qty, "qty": item.received_qty, "uom": item.uom, "stock_uom": item.uom, "rejected_qty": item.rejected_qty, "schedule_date": add_days(nowdate(), 7), "warehouse": lot_warehouse, "purchase_order": self.po})
		pr=frappe.get_doc({
			"supplier": self.supplier,
			"rejected_warehouse": rejected_warehouse,
			"set_warehouse": lot_warehouse,
			"is_subcontracted": po_doc.is_subcontracted,
			"supplier_warehouse": po_doc.supplier_warehouse,
			"doctype": "Purchase Receipt",
			"items": item_list })
		pr.save()
		pr.submit()
		return pr
	def get_po(self):
		if self.against_document.startswith("D"):
			self.po = frappe.db.get_value("Purchase Order",{'dc':self.against_document},'name')

def get_type(doctype, txt, searchfield, start, page_len, filters):
	if filters['type']=='DC':
		DC = []
		[DC.append([dc['name']]) for dc in frappe.get_list("DC", filters={'supplier': ['in',filters['supplier']],'lot':['in',filters['lot']]}, fields=["name"])]
		return DC
	else:
		PO=[]
		[PO.append([po['name']]) for po in frappe.get_list("Purchase Order", filters={'supplier': ['in',filters['supplier']],'lot':['in',filters['lot']]}, fields=["name"])]
		return PO
def get_Lot(doctype, txt, searchfield, start, page_len, filters):
	lot_list=[]
	[lot_list.append([lot['lot']]) for lot in frappe.get_list("Purchase Order", fields=["lot"]) if not lot['lot'] in lot_list]
	return lot_list
def get_supplier(doctype, txt, searchfield, start, page_len, filters):
	supplier_list = [] 
	[supplier_list.append([supplier['supplier']]) for supplier in frappe.get_list("Purchase Order", fields=["supplier"]) if not supplier['supplier'] in supplier_list]
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
	if doc_.startswith("D"):
		dc_doc=frappe.get_doc("DC",doc_)
		dc_process=dc_doc.process_1
		doc_ = frappe.db.get_value("Purchase Order",{'dc':doc_},'name')
	PO=frappe.get_doc("Purchase Order",doc_)
	if dc_process:
		apparelo_process=frappe.get_doc("Apparelo Process",dc_process)
	for item in PO.items:
		item_detail = frappe.get_doc('Item', item.item_code)
		if apparelo_process:
			return_materials.append({"item_code":item.item_code,"uom":item.uom,"qty":item.qty,"pf_item_code":item_detail.print_code,"secondary_uom":apparelo_process.in_secondary_uom})
		else:
			return_materials.append({"item_code":item.item_code,"uom":item.uom,"qty":item.qty,"pf_item_code":item_detail.print_code,"secondary_uom":item.uom})
	return return_materials

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
			item_list.append({"item_code": item.item_code, "received_qty": item.received_qty, "qty": item.received_qty - item.rejected_qty, "uom": item.uom, "stock_uom": item.uom, "rejected_qty": item.rejected_qty, "schedule_date": add_days(nowdate(), 7), "warehouse": lot_warehouse, "purchase_order": self.po})
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
		if po_.lot:
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
	dc_process=None
	apparelo_process=None
	if doc_.startswith("D"):
		all_po=frappe.db.get_all("Purchase Order")
		for po in all_po:
			po_=frappe.get_doc("Purchase Order",po.name)
			if po_.dc==doc_:
				doc_=po_.name
				dc_doc=frappe.get_doc("DC",po_.dc)
				dc_process=dc_doc.process_1
				break
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

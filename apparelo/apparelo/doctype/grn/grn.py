# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GRN(Document):
	def on_submit(self):
		pass
def get_DC(doctype, txt, searchfield, start, page_len, filters):
	DC=[]
	all_dc=frappe.db.get_all("DC")
	for dc in all_dc:
		dc_=frappe.get_doc("DC",dc.name)
		if dc_.supplier == filters['supplier']:
			DC.append([dc_.name])
	return DC
def get_Lot(doctype, txt, searchfield, start, page_len, filters):
	Lot=set()
	lot=[]
	all_dc=frappe.db.get_all("DC")
	for dc in all_dc:
		dc_=frappe.get_doc("DC",dc.name)
		if dc_.supplier == filters['supplier']:
			Lot.add(dc_.lot)
	for lot_ in Lot:
		lot.append([lot_])
	return lot

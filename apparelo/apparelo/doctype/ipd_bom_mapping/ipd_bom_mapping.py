# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IPDBOMMapping(Document):
	pass
def ipd_bom_mapping(ipd_list,ipd_name,item):
	ipd_bom=[]
	for ipd in ipd_list:
			for bom in ipd['BOM']:
				ipd_bom.append({'bom':bom,'ipd_process_index': ipd['index']})
	frappe.get_doc({
		'doctype': 'IPD BOM Mapping', 
		'item_production_details': ipd_name,
		'item': item,
		'bom_mapping':ipd_bom}).save()


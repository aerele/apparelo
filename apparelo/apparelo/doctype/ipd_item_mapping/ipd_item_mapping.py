# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IPDItemMapping(Document):
	pass
def ipd_item_mapping(ipd_list,ipd_name,item):
	ipd_item=[]
	for ipd in ipd_list:
		for variant in ipd['variants']:
			ipd_item.append({'item': variant,'ipd_process_index': ipd['index'],'ipd_input_index': ipd['input_index']})
	frappe.get_doc({
		'doctype': 'IPD Item Mapping', 
		'item_production_details': ipd_name,
		'item': item,
		'item_mapping':ipd_item}).save()



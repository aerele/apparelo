# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IPDItemMapping(Document):
	def get_process_variants(self, process):
		variants = []
		for item_mapping in self.item_mapping:
			if item_mapping.process_1 == process:
				variants.append(item_mapping.item)
		return variants
def ipd_item_mapping(ipd_list,ipd_name,item):
	ipd_item=[]
	for ipd in ipd_list:
		for variant in ipd['variants']:
			if ipd['process']=='Knitting':
				ipd_item.append({'item': variant, 'process_1':ipd['process'], 'input_item': ipd['input_item'][0], 'ipd_process_index': ipd['index'], 'input_index': ipd['input_index'], 'ipd': ipd['ipd']})
			else:
				ipd_item.append({'item': variant, 'process_1': ipd['process'], 'ipd_process_index': ipd['index'], 'input_index': ipd['input_index'], 'ipd': ipd['ipd']})
	ipd_item_=frappe.db.get_value("IPD Item Mapping",{'item_production_details': ipd_name},'name')
	if not ipd_item_:
		frappe.get_doc({
			'doctype': 'IPD Item Mapping',
			'item_production_details': ipd_name,
			'item': item,
			'item_mapping':ipd_item}).save()

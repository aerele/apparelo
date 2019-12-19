# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IPDItemMapping(Document):
	pass
def ipd_item_mapping(item,ipd_name,index):
	frappe.get_doc({
		'doctype': 'IPD Item Mapping', 
		'item': item, 
		'item_production_details': ipd_name,
		'ipd_process_index': index}).save()



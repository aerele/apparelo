# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IPDBOMMapping(Document):
	pass
def ipd_bom_mapping(bom,ipd_name):
	frappe.get_doc({
		'doctype': 'IPD BOM Mapping', 
		'bom': bom[0], 
		'item_production_details': ipd_name}).save()


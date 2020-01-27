# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloSize(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		item_attribute=frappe.get_doc("Item Attribute","Apparelo Size")
		sizes=[]  
		for value in item_attribute.item_attribute_values:
			sizes.append(value.attribute_value)
		if not self.size in sizes:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : self.size,
				"abbr" : self.size
			})
			item_attribute.save()

# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PrintType(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		item_attribute=frappe.get_doc("Item Attribute","Print Type")
		type_=[]  
		for value in item_attribute.item_attribute_values:
			type_.append(value.attribute_value)
		if not self.type in type_:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : self.type,
				"abbr" : self.type
			})
			item_attribute.save()


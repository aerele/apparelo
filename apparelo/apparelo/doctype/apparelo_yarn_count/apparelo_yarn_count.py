# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe

class AppareloYarnCount(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		item_attribute=frappe.get_doc("Item Attribute","Yarn Count")
		counts=[]  
		for value in item_attribute.item_attribute_values:
			counts.append(value.attribute_value)
		if not self.yarn_count in counts:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : self.yarn_count,
				"abbr" : self.yarn_count
			})
			item_attribute.save()

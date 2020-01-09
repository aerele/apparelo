# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloPart(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		item_attribute=frappe.get_doc("Item Attribute","Part")
		part=[]  
		for value in item_attribute.item_attribute_values:
			part.append(value.attribute_value)
		if not self.part_name in part:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : self.part_name,
				"abbr" : self.part_name
			})
		item_attribute.save()

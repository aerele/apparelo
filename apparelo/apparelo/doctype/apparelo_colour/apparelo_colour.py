# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloColour(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		item_attribute=frappe.get_doc("Item Attribute","Apparelo Colour")
		colours=[]
		colour = self.colour.strip()
		for value in item_attribute.item_attribute_values:
			colours.append(value.attribute_value)
		if not colour in colours:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : colour,
				"abbr" : colour
			})
			item_attribute.save()
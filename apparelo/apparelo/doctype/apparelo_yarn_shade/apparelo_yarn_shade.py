# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloYarnShade(Document):
	def validate(self):
		self.append_to_item_attribute()

	def append_to_item_attribute(self):
		item_attribute = frappe.get_doc("Item Attribute","Yarn Shade")
		yarn_shades = []
		yarn_shade = self.yarn_shade.strip()

		for value in item_attribute.item_attribute_values:
			yarn_shades.append(value.attribute_value)
		
		if not yarn_shade in yarn_shades:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : yarn_shade,
				"abbr" : yarn_shade
			})
			item_attribute.save()

def populate():
	if frappe.db.exists("Item Attribute", "Yarn Shade"):
		item_attribute = frappe.get_doc("Item Attribute", "Yarn Shade")
		for attr in item_attribute.item_attribute_values:
			apparelo_yarn_shade = frappe.new_doc("Apparelo Yarn Shade")
			apparelo_yarn_shade.yarn_shade = attr.attribute_value
			apparelo_yarn_shade.save()

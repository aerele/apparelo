# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloStyle(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		if not frappe.db.exists("Item Attribute", "Apparelo Style"):
			frappe.get_doc({
				"doctype": "Item Attribute",
				"attribute_name": "Apparelo Style",
				"item_attribute_values": []
			}).save()
		item_attribute=frappe.get_doc("Item Attribute","Apparelo Style")
		styles=[]  
		for value in item_attribute.item_attribute_values:
			styles.append(value.attribute_value)
		if not self.style in styles:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : self.style,
				"abbr" : self.style
			})
		item_attribute.save()
		if not frappe.db.exists("Item Attribute", "Apparelo Colour"):
			frappe.get_doc({
				"doctype": "Item Attribute",
				"attribute_name": "Apparelo Colour",
				"item_attribute_values": []
			}).save()
		color_attribute=frappe.get_doc("Item Attribute","Apparelo Colour")
		if not self.style in styles:
			color_attribute.append('item_attribute_values',{
				"attribute_value" : self.style,
				"abbr" : self.style
			})
		color_attribute.save()
		existing_doc=frappe.db.get_value('Apparelo Colour', {'colour': self.style}, 'name')
		if not existing_doc:
			color_doc=frappe.new_doc("Apparelo Colour")
			color_doc.colour=self.style
			color_doc.save()

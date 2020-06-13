# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloDia(Document):
	def validate(self):
		self.append_to_item_attribute()

	def append_to_item_attribute(self):
		item_attribute = frappe.get_doc("Item Attribute","Dia")
		dias=[]
		dia = self.dia.strip()

		for value in item_attribute.item_attribute_values:
			dias.append(value.attribute_value)
		
		if not dia in dias:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : dia,
				"abbr" : dia
			})
			item_attribute.save()

def populate():
	if not frappe.db.exists("Item Attribute", "Dia"):
		item_attribute = frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Dia",
			"item_attribute_values": []
		})
		for i in range(40, 165, 1):
			i = i * 0.25
			if int(str(i).split('.')[1]) == 0:
				i = str(i).split('.')[0]
			item_attribute.append('item_attribute_values',{
				"attribute_value" : str(i),
				"abbr" : str(i)
			})
		item_attribute.save()

		for i in range(40, 165, 1):
			i = i * 0.25
			if int(str(i).split('.')[1]) == 0:
				i = str(i).split('.')[0]
			apparelo_dia = frappe.new_doc("Apparelo Dia")
			apparelo_dia.dia = str(i)
			apparelo_dia.save()
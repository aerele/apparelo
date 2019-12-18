# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Ironing(Document):
	def on_submit(self):
		create_item_template(self)
	def create_variants(self, input_item_names):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = create_variants('Ironed Cloth', attribute_set)
		return list(set(variants))
	def create_boms(self, input_item_names, variants):
		item_list = []
		boms = []
		for input_item in input_item_names:
			item_list.append({"item_code": input_item,"uom": "Nos"})
		existing_bom = frappe.db.get_value('BOM', {'item': variants[0]}, 'name')
		if not existing_bom:
			bom = frappe.get_doc({
				"doctype": "BOM",
				"currency": get_default_currency(),
				"item": variants[0],
				"company": get_default_company(),
				"items": item_list
			})
			bom.save()
			bom.submit()
			boms.append(bom.name)
		else:
			boms.append(existing_bom)
		return boms

def create_item_template(self):
	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": self.item+" Ironed Cloth",
		"item_name": self.item+" Ironed Cloth",
		"description":self.item+" Ironed Cloth",
		"item_group": "Sub Assemblies",
		"stock_uom" : "Kg",
		"has_variants" : "1",
		"variant_based_on" : "Item Attribute",
		"attributes" : [
			{
				"attribute" : "Yarn Shade" 
			},
			{
				"attribute" : "Yarn Category"
			},
			{
			
				"attribute" : "Yarn Count"
			},
			{
				"attribute" : "Dia" 
			},
			{
				"attribute" : "Knitting Type"
			},
			{
				"attribute" : "Apparelo Colour" 
			},
			{
				"attribute" : "Part" 
			},
			{
				"attribute" : "Apparelo Size"
			}
		]
	})
	item.save()

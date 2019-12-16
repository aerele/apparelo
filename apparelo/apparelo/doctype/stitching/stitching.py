# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from erpnext import get_default_company, get_default_currency

class Stitching(Document):
	def on_submit(self):
		create_item_template(self)

	def create_variants(self, input_item_names):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = []
		parts = attribute_set["Part"]
		print('#*****************#')
		print(input_item_names,attribute_set,parts)
		for part in parts:
			variant_attribute_set = {}
			variant_attribute_set['Apparelo Colour'] = self.get_attribute_values('Apparelo Colour', part)
			variant_attribute_set['Apparelo Size'] = attribute_set["Apparelo Size"]
			variants.extend(create_variants(self.item+" Stitched Cloth", variant_attribute_set))
		return list(set(variants))

	def validate_attribute_values(self, attribute_name, input_attribute_values):
		return set(input_attribute_values).issubset(self.get_attribute_values(attribute_name))

	def get_attribute_values(self, attribute_name, part=None):
		attribute_value = set()

		if attribute_name == "Apparelo Colour":
			if part == None:
				for colour_mapping in self.colour_mappings:
					attribute_value.add(colour_mapping.part_colour)
			elif part:
				for colour_mapping in self.colour_mappings:
					if colour_mapping.part == part:
						attribute_value.add(colour_mapping.part_colour)

		return list(attribute_value)

	def create_boms(self, input_item_names, variants):
		item_list = []
		boms = []
		for input_item in input_item_names:
			item_list.append({"item_code": input_item,"uom": "Nos"})
		print(item_list)
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
	if not frappe.db.exists("Item", self.item+" Stitched Cloth"):
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": self.item+" Stitched Cloth",
			"item_name": self.item+" Stitched Cloth",
			"description":self.item+" Stitched Cloth",
			"item_group": "Sub Assemblies",
			"stock_uom" : "Kg",
			"has_variants" : "1",
			"variant_based_on" : "Item Attribute",
			"attributes" : [
				{
					"attribute" : "Apparelo Colour"
				},
				{
					"attribute" : "Apparelo Size"
				}
			]
		})
		item.save()

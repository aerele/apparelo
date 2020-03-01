# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants

class Checking(Document):
	def on_submit(self):
		create_item_template(self)

	def create_variants(self, input_item_names,colour,item,final_process):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		if final_process=="Checking":
			attribute_set.pop("Apparelo Colour")
			variants = create_variants(item, attribute_set)
		else:
			variants = create_variants(self.item+" Checked Cloth", attribute_set)
		return variants

	def create_boms(self, input_item_names, variants, attribute_set,item_size,colours,piece_count,final_process):
		
		boms = []
		for variant in variants:
			item_list = []
			for input_item in input_item_names:
				for size in item_size:
					if final_process=="Checking":
						if size.upper() in input_item  and size.upper() in variant:
							item_list.append({"item_code": input_item,"uom": "Nos"})
					else:
						for colour in colours:
							if size.upper() in input_item  and size.upper() in variant and colour.upper() in input_item and colour.upper() in variant:
								item_list.append({"item_code": input_item,"uom": "Nos"})
			existing_bom = frappe.db.get_value('BOM', {'item': variant}, 'name')
			if not existing_bom:
				bom = frappe.get_doc({
					"doctype": "BOM",
					"currency": get_default_currency(),
					"item": variant,
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
	if not frappe.db.exists('Item',self.item+' Checked Cloth'):
		frappe.get_doc({
		"doctype": "Item",
		"item_code": self.item+" Checked Cloth",
		"item_name": self.item+" Checked Cloth",
		"description":self.item+" Checked Cloth",
		"item_group": "Sub Assemblies",
		"stock_uom" : "Nos",
		"has_variants" : "1",
		"variant_based_on" : "Item Attribute",
		"is_sub_contracted_item": "1",
		"attributes" : [
			{
				"attribute" : "Apparelo Colour"
			},
			{
				"attribute" : "Apparelo Size"
			}
		]
	}).save()


# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from erpnext import get_default_company, get_default_currency

class Compacting(Document):
	def on_submit(self):
		create_item_template()

	def create_variants(self, input_item_names):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		attribute_set.update(self.get_variant_values())
		variants = create_variants('Compacted Cloth', attribute_set)
		return variants

	def create_boms(self, input_item_names, variants):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		boms = []
		doc_values = self.get_variant_values()
		for item in input_items:
			attr = get_attr_dict(item.attributes)
			attr.update(doc_values)
			args_set = generate_keyed_value_combinations(attr)
			for attribute_values in args_set:
				variant = get_variant("Compacted Cloth", args=attribute_values)
				if variant in variants:
					# TODO: Check if bom already present active/default
					existing_bom = frappe.db.get_value('BOM', {'item': variant}, 'name')
					if not existing_bom:
						bom = frappe.get_doc({
							"doctype": "BOM",
							"currency": get_default_currency(),
							"item": variant,
							"company": get_default_company(),
							"quantity": self.output_qty,
							"uom": self.output_uom,
							"items": [
								{
									"item_code": item.name,
									"qty": self.input_qty,
									"uom": self.input_uom,
									"rate": 0.0,
								}
							]
						})
						bom.save()
						bom.submit()
						boms.append(bom.name)
					else:
						boms.append(existing_bom)
				else:
					frappe.throw(_("unexpected error while creating BOM. Expected variant not found in list of supplied Variants"))
		return boms

	def get_variant_values(self):
		attribute_set = {}
		variant_to_dia = []
		for to_dia in self.dia_conversions:
			if int(str(float(to_dia.to_dia)).split('.')[1]) > 0:
				variant_to_dia.append(to_dia.to_dia)
			else:
				variant_to_dia.append(int(str(to_dia.to_dia).split('.')[0]))
		attribute_set['Dia']=variant_to_dia
		return attribute_set

def create_item_template():
	# todo: need to check if an item already exists with the same name
	dia = frappe.get_doc('Item Attribute', 'Dia')
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Compacted Cloth",
		"item_name": "Compacted Cloth",
		"description": "Compaced Cloth",
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
				"attribute" : "Dia",
				"numeric_value": 1,
				"from_range": dia.from_range,
				"to_range": dia.to_range,
				"increment": dia.increment
			},
			{
				"attribute" : "Knitting Type"
			},
			{
				"attribute" : "Apparelo Colour" 
			}
		]
	})
	item.save()

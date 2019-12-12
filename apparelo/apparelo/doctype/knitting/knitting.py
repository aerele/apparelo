# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants
from apparelo.apparelo.utils.utils import is_similar_bom
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from erpnext import get_default_company, get_default_currency

class Knitting(Document):
	def on_submit(self):
		create_item_template()

	def create_variants(self, input_item_names):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		attribute_set.update(self.get_variant_values())
		variants = create_variants('Knitted Cloth', attribute_set)
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
				variant = get_variant("Knitted Cloth", args=attribute_values)
				if variant in variants:
					bom_for_variant = frappe.get_doc({
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
					existing_bom_name = frappe.db.get_value('BOM', {'item': variant, 'docstatus': 1, 'is_active': 1}, 'name')
					if not existing_bom_name:
						bom_for_variant.save()
						bom_for_variant.submit()
						boms.append(bom_for_variant.name)
					else:
						existing_bom = frappe.get_doc('BOM', existing_bom_name)
						similar_diff = is_similar_bom(existing_bom, bom_for_variant)
						if similar_diff:
							boms.append(existing_bom_name)
						else:
							frappe.throw(_("Active BOM with different Materials or qty already exists for the item {0}. Please make these BOMs inactive and try again.").format(variant))
				else:
					frappe.throw(_("Unexpected error while creating BOM. Expected variant not found in list of supplied variants"))
		return boms

	def get_variant_values(self):
		attribute_set = {}
		attribute_set['Knitting Type'] = [self.type]
		variant_dia = []
		for dia in self.dia:
			# Happend to use whole number if the decimal is zero
			if int(str(float(dia.dia)).split('.')[1]) > 0:
				variant_dia.append(dia.dia)
			else:
				variant_dia.append(int(str(dia.dia).split('.')[0]))
		attribute_set['Dia'] = variant_dia
		return attribute_set

def create_item_template():
	if not frappe.db.exists("Item Attribute", "Yarn Shade"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Yarn Shade",
			"item_attribute_values": [
				{
					"attribute_value" : "Plain",
					"abbr" : "Plain"
				},
				{
					"attribute_value" : "A.Melange",
					"abbr" : "A.Melange"
				},
				{
					"attribute_value" : "G.Melange",
					"abbr" : "G.Melange"
				}
			]
		}).save()
	
	if not frappe.db.exists("Item Attribute", "Yarn Category"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Yarn Category",
			"item_attribute_values": [
				{
					"attribute_value" : "Green Label",
					"abbr" : "Green Label"
				},
				{
					"attribute_value" : "Violet Label",
					"abbr" : "Violet Label"
				},
				{
					"attribute_value" : "Red Label",
					"abbr" : "Red Label"
				}
			]
		}).save()
	
	if not frappe.db.exists("Item Attribute", "Yarn Count"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Yarn Count",
			"item_attribute_values": [
				{
					"attribute_value" : "30'S",
					"abbr" : "30'S"
				},
				{
					"attribute_value" : "34'S",
					"abbr" : "34'S"
				},
				{
					"attribute_value" : "36'S",
					"abbr" : "36'S"
				},
				{
					"attribute_value" : "40'S",
					"abbr" : "40'S"
				}
			]
		}).save()

	if not frappe.db.exists("Item Attribute", "Dia"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Dia",
			"numeric_values": 1,
			"from_range": 18.0,
			"to_range": 36.0,
			"increment": 0.25
		}).save()
	if not frappe.db.exists("Item Attribute", "Knitting Type"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Knitting Type",
			"item_attribute_values": [
				{
					"attribute_value" : "Single Rib",
					"abbr" : "Single Rib"
				},
				{
					"attribute_value" : "Fine",
					"abbr" : "Fine"
				},
				{
					"attribute_value" : "Single Rib (Fold)",
					"abbr" : "Single Rib (Fold)"
				},
				{
					"attribute_value" : "Fine (Fold)",
					"abbr" : "Fine (Fold)"
				}
			]
		}).save()

	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Yarn",
		"item_name": "Yarn",
		"description": "Yarn",
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
			}
		]
	})
	item.save()

	dia = frappe.get_doc('Item Attribute', 'Dia')
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Knitted Cloth",
		"item_name": "Knitted Cloth",
		"description": "Knitted Cloth",
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
				"attribute" : "Dia" ,
				"numeric_values": 1,
				"from_range": dia.from_range,
				"to_range": dia.to_range,
				"increment": dia.increment
			},
			{
				"attribute" : "Knitting Type"
			}
		]
	})
	item.save()

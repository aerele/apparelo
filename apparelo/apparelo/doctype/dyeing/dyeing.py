# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from apparelo.apparelo.utils.utils import is_similar_bom
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants

class Dyeing(Document):
	def on_submit(self):
		create_item_template()
		create_item_attribute()

	def create_variants(self, input_item_names):
		new_variants=[]
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes,input_items)))
		attribute_set.update(self.get_variant_values())
		variants = create_variants('Dyed cloth', attribute_set)
		for dia in attribute_set["Dia"]:
			for variant in variants:
				if str(dia) in variant:
					if not str(dia)+" Dia" in variant:
						new_variant=variant.replace(str(dia),str(dia)+" Dia")
						r_variant=frappe.rename_doc("Item",variant,new_variant)
						new_variants.append(r_variant)
		if len(new_variants)==0:
			new_variants=variants
		return new_variants

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
				variant = get_variant('Dyed cloth',args=attribute_values)
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
		variant_colour = []
		for colour in self.colours:
			variant_colour.append(colour.colour)
		attribute_set['Apparelo Colour'] = variant_colour
		return attribute_set

def create_item_attribute():
	if not frappe.db.exists("Item Attribute", "Apparelo Colour"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Apparelo Colour",
			"item_attribute_values": [
				{
					"attribute_value" : "Red",
					"abbr" : "Red"
				},
				{
					"attribute_value" : "Blue",
					"abbr" : "Blue"
				},
				{
					"attribute_value" : "Green",
					"abbr" : "Green"
				},
				{
					"attribute_value" : "Black",
					"abbr" : "Black"
				},
				{
					"attribute_value" : "Navy",
					"abbr" : "Navy"
				},
				{
					"attribute_value" : "A.Mel",
					"abbr" : "A.Mel"
				},
				{
					"attribute_value" : "G.Mel",
					"abbr" : "G.Mel"
				},
				{
					"attribute_value" : "Grey",
					"abbr" : "Grey"
				},
				{
					"attribute_value" : "Brown",
					"abbr" : "Brown"
				},
				{
					"attribute_value" : "Maroon",
					"abbr" : "Maroon"
				}
			]
		}).save()

def create_item_template():
	dia = frappe.get_doc('Item Attribute', 'Dia')
	if not frappe.db.exists('Item','Dyed Cloth'):
		frappe.get_doc({
			"doctype": "Item",
			"item_code": "Dyed Cloth",
			"item_name": "Dyed Cloth",
			"description": "Dyed Cloth",
			"item_group": "Sub Assemblies",
			"stock_uom" : "Kg",
			"has_variants" : "1",
			"variant_based_on" : "Item Attribute",
			"is_sub_contracted_item": "1",
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
				},
				{
					"attribute" : "Apparelo Colour"
				}
			]
		}).save()

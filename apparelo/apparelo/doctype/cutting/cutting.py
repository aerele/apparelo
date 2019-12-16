# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants
from frappe.model.document import Document
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from erpnext import get_default_company, get_default_currency

class Cutting(Document):
	def on_submit(self):
		create_item_attribute()
		create_item_template(self)

	def create_variants(self, input_item_names):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = []
		for colour_mapping in self.colour_mapping:
			for detail in self.details:
				if colour_mapping.part==detail.part:
					if colour_mapping.colour==attribute_set["Apparelo Colour"][0] and str(int(detail.dia))==attribute_set["Dia"][0]:
						parts = list(self.get_attribute_values("Part"))
						for part in parts:
							variant_attribute_set = {}
							variant_attribute_set['Part'] = [part]
							variant_attribute_set['Apparelo Colour'] = self.get_attribute_values('Apparelo Colour', part)
							variant_attribute_set['Apparelo Size'] = self.get_attribute_values('Size', part)
							variants.extend(create_variants(self.item+" Cut Cloth", variant_attribute_set))
					else:
						frappe.throw(_("Cutting has more colours or Dia that is not available in the input"))
		return list(set(variants))

	def get_matching_details(self, part, size):
		# ToDo: Part Size combination may not be unique
		for detail in self.details:
			if detail.part == part[0] and detail.size == size[0]:
				return {"Dia": detail.dia, "Weight": detail.weight}

	def create_boms(self, input_item_names, variants):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		boms = []
		for variant in variants:
			var=frappe.get_doc('Item', variant)
			attr = get_attr_dict(var.attributes)
			attr.update(self.get_matching_details(attr["Part"], attr["Apparelo Size"]))
			for input_item in input_items:
				input_item_attr = get_attr_dict(input_item.attributes)
				if input_item_attr["Apparelo Colour"] == attr["Apparelo Colour"] and input_item_attr["Dia"] == attr["Dia"]:
					break
			existing_bom = frappe.db.get_value('BOM', {'item': variant}, 'name')
			if not existing_bom:
				bom = frappe.get_doc({
					"doctype": "BOM",
					"currency": get_default_currency(),
					"item": variant,
					"company": get_default_company(),
					"items": [
						{
							"item_code": input_item.name,
							"qty": attr["Weight"],
							"uom": 'Gram',
						}
					]
				})
				bom.save()
				bom.submit()
				boms.append(bom.name)
			else:
				boms.append(existing_bom)
		return boms

	def get_attribute_values(self, attribute_name, part=None):
		attribute_value = set()

		if attribute_name == "Apparelo Colour":
			if part == None:
				for colour_mapping in self.colour_mapping:
					attribute_value.add(colour_mapping.colour)
			elif part:
				for colour_mapping in self.colour_mapping:
					if colour_mapping.part == part:
						attribute_value.add(colour_mapping.colour)

		elif attribute_name == "Dia":
			for detail in self.details:
				if int(str(float(detail.dia)).split('.')[1]) > 0:
					attribute_value.add(str(detail.dia))
				else:
					attribute_value.add(str(detail.dia).split('.')[0])

		elif attribute_name == "Size":
			if part == None:
				for detail in self.details:
					attribute_value.add(detail.size)
			elif part:
				for detail in self.details:
					if detail.part == part:
						attribute_value.add(detail.size)

		elif attribute_name == "Part":
			for detail in self.details:
					attribute_value.add(detail.part)

		elif attribute_name == "weight":
			for detail in self.details:
					attribute_value.add(detail.weight)
		return list(attribute_value)

def create_item_attribute():
	if not frappe.db.exists("Item Attribute", "Part"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Part",
			"item_attribute_values": [
				{
					"attribute_value" : "Front",
					"abbr" : "Front"
				},
				{
					"attribute_value" : "Back",
					"abbr" : "Back"
				},
				{
					"attribute_value" : "Panel",
					"abbr" : "Panel"
				},
				{
					"attribute_value" : "Sleeve",
					"abbr" : "Sleeve"
				}
			]
		}).save()

	if not frappe.db.exists("Item Attribute", "Apparelo Size"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Apparelo Size",
			"item_attribute_values": [
				{
					"attribute_value" : "35 cm",
					"abbr" : "35 cm"
				},
				{
					"attribute_value" : "40 cm",
					"abbr" : "40 cm"
				},
				{
					"attribute_value" : "45 cm",
					"abbr" : "45 cm"
				},
				{
					"attribute_value" : "50 cm",
					"abbr" : "50 cm"
				},
				{
					"attribute_value" : "55 cm",
					"abbr" : "55 cm"
				},
				{
					"attribute_value" : "60 cm",
					"abbr" : "60 cm"
				},
				{
					"attribute_value" : "65 cm",
					"abbr" : "65 cm"
				},
				{
					"attribute_value" : "70 cm",
					"abbr" : "70 cm"
				},
				{
					"attribute_value" : "75 cm",
					"abbr" : "75 cm"
				},
				{
					"attribute_value" : "80 cm",
					"abbr" : "80 cm"
				},
				{
					"attribute_value" : "85 cm",
					"abbr" : "85 cm"
				},
				{
					"attribute_value" : "90 cm",
					"abbr" : "90 cm"
				},
				{
					"attribute_value" : "95 cm",
					"abbr" : "95 cm"
				},
				{
					"attribute_value" : "100 cm",
					"abbr" : "100 cm"
				},
				{
					"attribute_value" : "105 cm",
					"abbr" : "105 cm"
				},
				{
					"attribute_value" : "110 cm",
					"abbr" : "110 cm"
				},
				{
					"attribute_value" : "115 cm",
					"abbr" : "115 cm"
				}
			]
		}).save()

def create_item_template(self):
	# todo: need to check if an item already exists with the same name
	if not frappe.db.exists("Item", self.item+" Cut Cloth"):
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": self.item+" Cut Cloth",
			"item_name": self.item+" Cut Cloth",
			"description":self.item+" Cut Cloth",
			"item_group": "Sub Assemblies",
			"stock_uom" : "Kg",
			"has_variants" : "1",
			"variant_based_on" : "Item Attribute",
			"attributes" : [
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
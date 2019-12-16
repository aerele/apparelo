# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from erpnext import get_default_company, get_default_currency


class PiecePrinting(Document):
	def on_submit(self):
		create_item_template(self)
		
	def create_variants(self, input_item_names):
		print("***********")
		print(input_item_names)
		print("***********")
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name[0]))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = []
		#if self.validate_attribute_values("Apparelo Colour", attribute_set["Apparelo Colour"]) and self.validate_attribute_values("Dia",(attribute_set["Dia"])):
		parts = list(self.get_attribute_values("Part"))
		for part in parts:
			variant_attribute_set = {}
			variant_attribute_set['Part'] = [part]
			# variant_attribute_set['Apparelo Colour'] = self.get_attribute_values('Apparelo Colour', part)
			# variant_attribute_set['Apparelo Size'] = self.get_attribute_values('Size', part)
			variants.append(create_variants(self.item+" Printed Cloth", variant_attribute_set))
		# else:
			
		# 	frappe.throw(_("Cutting has more colours or Dia that is not available in the input"))
		return variants

	# def validate_attribute_values(self, attribute_name, input_attribute_values):
	# 	return set(input_attribute_values).issubset(self.get_attribute_values(attribute_name))

	def get_attribute_values(self, attribute_name, part=None):
		attribute_value = set()

		if attribute_name == "Part":
			for part in self.part:
					attribute_value.add(part.part)

		return list(attribute_value)

def create_item_template(self):
	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": self.item+" Printed Cloth",
		"item_name": self.item+" Printed Cloth",
		"description":self.item+" Printed Cloth",
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
# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from itertools import combinations
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.utils import validate_additional_parts_mapping
from apparelo.apparelo.utils.item_utils import (
	get_attr_dict, get_item_attribute_set, create_variants,
	create_additional_parts, matching_additional_part)


class Packing(Document):
	def on_submit(self):
		if self.enable_additional_parts:
			validate_additional_parts_mapping(self.additional_parts, self.additional_parts_size, self.additional_parts_colour)

	def create_variants(self, input_item_names, colour=None, item=None, final_process=None):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(
			list(map(lambda x: x.attributes, input_items)))
		if "Apparelo Colour" in attribute_set:
			attribute_set.pop('Apparelo Colour')
		variants = create_variants(item, attribute_set)
		return variants

	def create_boms(self, input_item_names, variants, colour, attribute_set=None, item_size=None, piece_count=None, final_item=None, final_process=None):
		boms = []
		if self.enable_additional_parts:
			additional_parts = create_additional_parts(
				self.additional_parts_colour, self.additional_parts_size, self.additional_parts)

		if piece_count == self.input_qty:
			for variant in variants:
				item_list = []
				variant_doc=frappe.get_doc("Item",variant)
				variant_attr = get_attr_dict(variant_doc.attributes)
				for input_item in input_item_names:
					input_item_doc=frappe.get_doc("Item",input_item)
					input_attr = get_attr_dict(input_item_doc.attributes)
					for size in item_size:
						if size in input_attr["Apparelo Size"] and size in variant_attr["Apparelo Size"]:
							item_list.append({
								"item_code": input_item,
								"uom": "Nos"
							})
				if self.enable_additional_parts:
					matched_part=matching_additional_part(additional_parts,self.additional_parts_colour,self.additional_parts_size,self.additional_parts,variant)
					for additional_ in self.additional_parts:
						if additional_.based_on=="None":
							item_list.append({"item_code": additional_.item,"qty":additional_.qty ,"uom": additional_.uom})
					item_list.extend(matched_part)
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
		if self.input_qty > piece_count:
			if self.input_qty % piece_count == 0:
				repeating_count = self.input_qty // piece_count
				for variant in variants:
					item_list = []
					variant_doc=frappe.get_doc("Item",variant)
					variant_attr = get_attr_dict(variant_doc.attributes)
					for input_item in input_item_names:
						input_item_doc=frappe.get_doc("Item",input_item)
						input_attr = get_attr_dict(input_item_doc.attributes)
						for size in item_size:
							if size in input_attr["Apparelo Size"] and size in variant_attr["Apparelo Size"]:
								item_list.append({
									"item_code": input_item,
									"uom": "Nos",
									"qty": repeating_count
								})
					if self.enable_additional_parts:
						matched_part = matching_additional_part(
							additional_parts, self.additional_parts_colour,
							self.additional_parts_size, self.additional_parts, variant)
						for additional_part in self.additional_parts:
							if additional_part.based_on == "None":
								item_list.append({
									"item_code": additional_part.item,
									"qty": additional_part.qty,
									"uom": additional_part.uom
								})
						item_list.extend(matched_part)
					existing_bom = frappe.db.get_value(
						'BOM', {'item': variant}, 'name')
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
			else:
				frappe.throw(_("Invalid Input Quantity"))
		if self.input_qty < piece_count:
			colours = list(combinations(colour, self.input_qty))
			create_item_combo_attribute(colours)
			create_item_combo_template(final_item)
			combo_variants = create_combo_variant(
				final_item, colours, item_size)
			for variant in combo_variants:
				variant_doc = frappe.get_doc("Item", variant)
				variant_attr = get_attr_dict(variant_doc.attributes)
				for attribute_ in variant_doc.attributes:
					if attribute_.attribute == "Apparelo Size":
						size = attribute_.attribute_value
					if attribute_.attribute == "Combo":
						combo = attribute_.attribute_value
				item_list_ = []
				for items in input_item_names:
					input_item_doc=frappe.get_doc("Item",items)
					input_attr = get_attr_dict(input_item_doc.attributes)
					if size in variant_attr["Apparelo Size"] and size in input_attr["Apparelo Size"]:
						for color in combo.split(","):
							if color in input_attr["Apparelo Colour"]:
								item_list_.append({
									"item_code": items,
									"uom": "Nos"
								})
				if self.enable_additional_parts:
					matched_part=matching_additional_part(additional_parts,self.additional_parts_colour,self.additional_parts_size,self.additional_parts,variant)
					for additional_part in self.additional_parts:
						if additional_part.based_on=="None":
							item_list_.append({"item_code": additional_part.item,"qty":additional_part.qty ,"uom": additional_part.uom})
					item_list_.extend(matched_part)
				existing_bom = frappe.db.get_value(
					'BOM', {'item': variant}, 'name')
				if not existing_bom:
					new_bom = frappe.get_doc({
						"doctype": "BOM",
						"currency": get_default_currency(),
						"uom": "Nos",
						"item": variant,
						"company": get_default_company(),
						"items": item_list_
					})
					new_bom.save()
					new_bom.submit()
				else:
					continue
			for variant in variants:
				items_ = []
				variant_doc = frappe.get_doc("Item", variant)
				variant_attr = get_attr_dict(variant_doc.attributes)
				for variant_ in combo_variants:
					combo_variant_doc = frappe.get_doc("Item", variant_)
					combo_variant_attr = get_attr_dict(combo_variant_doc.attributes)
					for size in item_size:
						if size in variant_attr["Apparelo Size"] and size in combo_variant_attr["Apparelo Size"]:
							items_.append({
								"item_code": variant_,
								"uom": "Nos",
								"bom_no": get_item_details(variant_).get("bom_no")
							})
				existing_bom_ = frappe.db.get_value(
					'BOM', {'item': variant}, 'name')
				if not existing_bom_:
					bom = frappe.get_doc({
						"doctype": "BOM",
						"currency": get_default_currency(),
						"uom": "Nos",
						"is_default": 1,
						"item": variant,
						"company": get_default_company(),
						"items": items_
					})

					bom.save()
					bom.submit()
					boms.append(bom.name)
				else:
					boms.append(existing_bom_)
		return boms


def create_combo_variant(final_item, colours, size):
	"""Return the combo variants."""
	combo_variants = []
	item_attribute = frappe.get_doc("Item Attribute", "Combo")
	count = 0
	for size_ in size:
		for attribute_ in colours:
			attr = ''
			for color in sorted(attribute_):
				attr += color+","
			combo = []
			for value in item_attribute.item_attribute_values:
				combo.append(value.attribute_value)
			count = len(combo)+1
			if attr[:-1]not in combo:
				item_attribute.append('item_attribute_values', {
					"attribute_value": attr[:-1],
					"abbr": "Combo "+str(count)
					})
				item_attribute.save()
			attribute = {"Apparelo Size": [size_], "Combo": [attr[:-1]]}
			combo_variants.extend(create_variants(
				final_item+" Combo Cloth", attribute))
	return combo_variants


def create_item_combo_attribute(colours):
	if not frappe.db.exists("Item Attribute", "Combo"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Combo",
			"item_attribute_values": []
		}).save()


def create_item_combo_template(final_item):
	if not frappe.db.exists("Item", final_item+" Combo Cloth"):
		frappe.get_doc({
			"doctype": "Item",
			"item_code": final_item+" Combo Cloth",
			"item_name": final_item+" Combo Cloth",
			"description": final_item+" Combo Cloth",
			"item_group": "Sub Assemblies",
			"stock_uom": "Nos",
			"has_variants": "1",
			"variant_based_on": "Item Attribute",
			"is_sub_contracted_item": "1",
			"attributes": [
				{
					"attribute": "Combo"
				},
				{
					"attribute": "Apparelo Size"
				}
			]
		}).save()

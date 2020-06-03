# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.core.doctype.version.version import get_diff
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant, create_variant

stock_settings_doc = frappe.get_doc("Stock Settings")
def create_variants(item_template, args):
	args_set = generate_keyed_value_combinations(args)
	variants = []
	for attribute_values in args_set:
		existing_variant = get_variant(item_template, args=attribute_values)
		if not existing_variant:
			variant = create_variant(item_template, attribute_values)
			variant.over_delivery_receipt_allowance = stock_settings_doc.over_delivery_receipt_allowance
			variant.save()
			variants.append(variant.name)
		else:
			variants.append(existing_variant)
	return variants
def create_additional_variants(item_template, args,qty,uom):
	args_set = generate_keyed_value_combinations(args)
	variants = []
	for attribute_values in args_set:
		additional_parts={}
		existing_variant = get_variant(item_template, args=attribute_values)
		if not existing_variant:
			variant = create_variant(item_template, attribute_values)
			variant.save()
			additional_parts['item_code']=variant.name
			additional_parts['qty']=qty
			additional_parts['uom']=uom
			variants.append(additional_parts)
		else:
			additional_parts['item_code']=existing_variant
			additional_parts['qty']=qty
			additional_parts['uom']=uom
			variants.append(additional_parts)
	return variants


def get_attr_dict(attrs):
	attribute_set = {}
	for attribute in attrs:
		attribute_set[attribute.attribute] = [attribute.attribute_value]
	return attribute_set

def get_item_attribute_set(item_attribute_arrays):
	attribute_set = {}
	for item_attr_array in item_attribute_arrays:
		attr_set = get_attr_dict(item_attr_array)
		for attr in attr_set:
			if attr in attribute_set:
				attribute_set[attr].extend(attr_set[attr])
				attribute_set[attr] = list(set(attribute_set[attr]))
			else:
				attribute_set[attr] = attr_set[attr]
	return attribute_set


def is_similar_bom(bom1, bom2):
	diff = get_bom_diff(bom1, bom2)
	for key in diff.changed:
		if key[0] in ["quantity", "uom"]:
			return False
	for row in diff.row_changed:
		if row[0] == "items":
			for key in row[3]:
				if key[0] in ["qty", "uom", "rate"]:
					return False
	return True


def get_bom_diff(bom1, bom2):
	from frappe.model import table_fields

	out = get_diff(bom1, bom2)
	out.row_changed = []
	out.added = []
	out.removed = []

	meta = bom1.meta

	identifiers = {
		'operations': 'operation',
		'items': 'item_code',
		'scrap_items': 'item_code',
		'exploded_items': 'item_code'
	}

	for df in meta.fields:
		old_value, new_value = bom1.get(df.fieldname), bom2.get(df.fieldname)

		if df.fieldtype in table_fields:
			identifier = identifiers[df.fieldname]
			# make maps
			old_row_by_identifier, new_row_by_identifier = {}, {}
			for d in old_value:
				old_row_by_identifier[d.get(identifier)] = d
			for d in new_value:
				new_row_by_identifier[d.get(identifier)] = d

			# check rows for additions, changes
			for i, d in enumerate(new_value):
				if d.get(identifier) in old_row_by_identifier:
					diff = get_diff(old_row_by_identifier[d.get(identifier)], d, for_child=True)
					if diff and diff.changed:
						out.row_changed.append((df.fieldname, i, d.get(identifier), diff.changed))
				else:
					out.added.append([df.fieldname, d.as_dict()])

			# check for deletions
			for d in old_value:
				if not d.get(identifier) in new_row_by_identifier:
					out.removed.append([df.fieldname, d.as_dict()])

	return out

def create_additional_parts(colors,sizes,items):
	additional_parts=[]
	for item in items:
		attribute_set={}
		colors_=[]
		sizes_=[]
		if item.based_on=="Size and Colour":
			for size in sizes:
				for color in colors:
					if item.item == size.item and item.item == color.item:
						if not color.part_colour in colors_:
							colors_.append(color.part_colour)
						if not size.part_size  in sizes_:
							sizes_.append(size.part_size)
			attribute_set["Apparelo Colour"]=colors_
			attribute_set["Apparelo Size"]=sizes_
			additional_parts.extend(create_additional_variants(item.item,attribute_set,item.qty,item.uom))
		if item.based_on=="Size":
			for size in sizes:
				if item.item ==size.item:
					if not size.part_size  in sizes_:
						sizes_.append(size.part_size)
			attribute_set["Apparelo Size"]=sizes_
			additional_parts.extend(create_additional_variants(item.item,attribute_set,item.qty,item.uom))
		if item.based_on=="Colour":
			for color in colors:
				if item.item ==color.item:
					if not color.part_colour in colors_:
						colors_.append(color.part_colour)
			attribute_set["Apparelo Colour"]=colors_
			additional_parts.extend(create_additional_variants(item.item,attribute_set,item.qty,item.uom))
	return additional_parts

def matching_additional_part(additional_parts,colors,sizes,items,variant):
	matched_part=[]
	variant_doc=frappe.get_doc("Item",variant)
	variant_attr = get_attr_dict(variant_doc.attributes)
	for additional_part in additional_parts:
		input_item_doc=frappe.get_doc("Item",additional_part['item_code'])
		input_attr = get_attr_dict(input_item_doc.attributes)
		for item in items:
			if item.item in additional_part['item_code']:
				if item.based_on=="Size and Colour":
					for size in sizes:
						for color in colors:
							if item.item == size.item and item.item == color.item:
								if color.piece_colour in variant_attr["Apparelo Colour"] and size.piece_size in variant_attr["Apparelo Size"] and color.part_colour in input_attr['Apparelo Colour'] and size.part_size in input_attr["Apparelo Size"]:
									matched_part.append(additional_part)
				if item.based_on=="Size":
					for size in sizes:
						if item.item ==size.item:
							if size.piece_size in variant_attr["Apparelo Size"] and size.part_size in input_attr["Apparelo Size"]:
								matched_part.append(additional_part)
				if item.based_on=="Colour":
					for color in colors:
						if item.item ==color.item:
							if color.piece_colour in variant_attr["Apparelo Colour"] and color.part_colour in input_attr["Apparelo Colour"]:
								matched_part.append(additional_part)
	return matched_part

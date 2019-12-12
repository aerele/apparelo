# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant, create_variant

def create_variants(item_template, args):
	args_set = generate_keyed_value_combinations(args)
	variants = []
	for attribute_values in args_set:
		existing_variant = get_variant(item_template, args=attribute_values)
		if not existing_variant:
			variant = create_variant(item_template, attribute_values)
			variant.save()
			variants.append(variant.name)
		else:
			variants.append(existing_variant)

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



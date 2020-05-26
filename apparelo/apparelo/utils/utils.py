# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.core.doctype.version.version import get_diff
from frappe import _
import collections
from frappe.utils import cint

def is_similar_bom(bom1, bom2):
	diff = get_bom_diff(bom1, bom2)
	for key in diff.changed:
		if key[0] in ["quantity", "uom"]:
			return False
	for row in diff.row_changed:
		if row[0] == "items":
			for key in row[3]:
				if key[0] in ["qty", "uom"]:
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


def generate_printable_list(items, grouping_params):
	""" This function generates simple printable objects from items list with quantities
	by applying the parameters provided.

	:param items: list of items containing following keys- item_code, qty, uom, secondary_qty, secondary_uom
	:param grouping_params: A list of dicts with the following keys: dimension, group_by, attribute_list

	Description for the keys in the grouping_params dict:
	dimension: item attributes by which qty should be calculated. format - (dimension1, dimension2)
	group_by: list of item attributes for which sepearate tables should be generated
	"""

	# getting item attributes for all the items
	item_attributes_serial_list = frappe.get_list(
		"Item",
		filters={'item_code': ['in', [x.item_code for x in items]]},
		fields=[
			"item_code",
			"`tabItem Variant Attribute`.attribute",
			"`tabItem Variant Attribute`.attribute_value"
			]
		)
	item_list_with_attributes = {}
	for single_item_attribute in item_attributes_serial_list:
		if single_item_attribute.item_code not in item_list_with_attributes:
			item_list_with_attributes[single_item_attribute.item_code] = {single_item_attribute.attribute: single_item_attribute.attribute_value, 'attribute_list': [single_item_attribute.attribute]}
		else:
			item_list_with_attributes[single_item_attribute.item_code].update({single_item_attribute.attribute: single_item_attribute.attribute_value})
			item_list_with_attributes[single_item_attribute.item_code]['attribute_list'].append(single_item_attribute.attribute)

	# generating the desired item format
	item_dict_list = []
	for item in items:
		temp_item = {
			"item_code": item.item_code,
			"pf_item_code": item.pf_item_code,
			"secondary_qty": item.secondary_qty,
			"secondary_uom": item.secondary_uom
		}
		temp_item['qty'] = item.qty if hasattr(item, 'qty') else item.quantity
		temp_item['uom'] = item.uom if hasattr(item, 'uom') else item.primary_uom
		temp_item.update(item_list_with_attributes[item.item_code])
		temp_item['attribute_list'].sort()
		item_dict_list.append(temp_item)

	# generating the printable list
	final_printable_list = []
	for attribute_list, group in groupby_unsorted(item_dict_list, key=lambda x: tuple(x['attribute_list'])):
		try:
			grouping_param = next(param for param in grouping_params if sort_and_return(param['attribute_list']) == list(attribute_list))
		except StopIteration:
			grouping_param = {
				"dimension": (None, None),
				"group_by": [],
				"attribute_list": attribute_list}
		group_by = grouping_param['group_by']
		dimension = grouping_param['dimension']
		for key, group2 in groupby_unsorted(list(group), key=lambda x: get_values_as_tuple(x, group_by)):
			# this table_title data structure to be changed later as per jinja requirements
			table_title = frappe._dict({
				'attributes': group_by,
				'attribute_values': key
			})
			section_title = None
			header_column = []
			header_row = []
			data = []
			temp_data = {}
			if dimension == (None, None):
				dimension = ('item_code', None)
			for key, table_group in groupby_unsorted(list(group2), key=lambda x: get_values_as_tuple(x, dimension)):
				table_group = list(table_group)
				if not header_column or not header_row:
					if dimension[0] is not None and dimension[1] is not None:
						header_column = [dimension[0]]
						header_row = [dimension[1]]
					elif dimension[0] is not None and dimension[0] != 'item_code':
						header_column = [dimension[0]]
						header_row = [dimension[0], 'Qty']
					elif dimension[1] is not None:
						header_column = [dimension[1], 'Qty']
						header_row = [dimension[1]]
					elif dimension[0] == 'item_code':
						header_column = ['Item']
						header_row = ['Item', 'Qty']
				key_0 = key[0]
				if dimension[0] == 'item_code':
					key_0 = table_group[0]['pf_item_code']
				column_index = 1
				row_index = 1
				if key_0 is not None:
					row_index = header_column.index(key_0) if key_0 in header_column else None
					if row_index is None:
						header_column.append(key_0)
						row_index = len(header_column)-1
				if key[1] is not None:
					column_index = header_row.index(key[1]) if key[1] in header_row else None
					if column_index is None:
						header_row.append(key[1])
						column_index = len(header_row)-1
				qty = get_sum_from_dict_list(table_group, 'qty')
				secondary_qty = get_sum_from_dict_list(table_group, 'secondary_qty')
				uom = check_if_same_value_dict_list(table_group, 'uom')
				secondary_uom = check_if_same_value_dict_list(table_group, 'secondary_uom')
				if f'r{column_index}c{row_index}' not in temp_data:
					temp_data[f'r{column_index}c{row_index}'] = frappe._dict({
						'qty': qty,
						'uom': uom,
						'secondary_qty': secondary_qty,
						'secondary_uom': secondary_uom
					})
				else:
					frappe.throw(_(f"Data overlap when generation print table for position r{column_index}c{row_index}. Key: ({key[0]},{key[1]}). Dimension: ({dimension[0]},{dimension[1]})."))
			for row_index in range(1, len(header_column)):
				tmp_column = []
				for column_index in range(1, len(header_row)):
					tmp_column.append(temp_data[f'r{column_index}c{row_index}'] if f'r{column_index}c{row_index}' in temp_data else None)
				data.append(tmp_column)
			table_object = frappe._dict({
				'data': data,
				'header_row': header_row,
				'header_column': header_column,
				'table_title': table_title,
				'section_title': section_title
			})
			final_printable_list.append(table_object)
	return final_printable_list


def generate_html_from_list(printable_list):
	context = frappe._dict({'context':printable_list})
	return frappe.utils.jinja.render_template(
		"apparelo/apparelo/utils/items_table_print.html",
		context,
		is_path=True
		)


def groupby_unsorted(seq, key=lambda x: x):
	indexes = collections.defaultdict(list)
	for i, elem in enumerate(seq):
		indexes[key(elem)].append(i)
	for k, idxs in indexes.items():
		yield k, (seq[i] for i in idxs)


def get_values_as_tuple(input_dict, keys):
	values_list = []
	for key in keys:
		if key and key in input_dict:
			values_list.append(input_dict[key])
		else:
			values_list.append(key)
	return tuple(values_list)


def sort_and_return(l):
	l.sort()
	return l


def get_sum_from_dict_list(dict_list, key):
	val_sum = 0
	for elem in dict_list:
		try:
			val = float(elem[key])
		except:
			val = cint(elem[key])
		val_sum += val
	return val_sum


def check_if_same_value_dict_list(dict_list, key):
	first = None
	flag = False
	for elem in dict_list:
		if not flag:
			first = elem[key]
			flag = True
		if first != elem[key]:
			return False
	return first

# things to figureout
	# - how to separate out different tables for different size sets

# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from frappe import _
from six import string_types, iteritems
from frappe.model.document import Document
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants
from erpnext.stock.get_item_details import get_conversion_factor
from collections import Counter
from apparelo.apparelo.utils.utils import validate_table_fields

class Cutting(Document):
	def on_submit(self):
		create_item_attribute()
		result, value = validate_table_fields(self.colour_mapping, self.details, 'Cutting')
		if not result:
			frappe.throw(_(f'The part {value} entered in colour mapping table was not found in details table.'))
		result, value = validate_table_fields(self.details, self.colour_mapping, 'Cutting')
		if not result:
			frappe.throw(_(f'The part {value} entered in details table was not found in colour mapping table.'))


	def create_variants(self, input_item_names, size, item):
		cutting_attribute={}
		input_items = []
		cutting_size = []
		for input_item_name in set(input_item_names):
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = []
		if self.attribute_validate("Apparelo Colour", attribute_set["Apparelo Colour"]) and self.attribute_validate("Dia", attribute_set["Dia"]):
			parts = set(self.get_attribute_values("Part"))
			variant_attribute_set = {}
			for part in parts:
				new_cutting_size = []
				variant_attribute_set['Part'] = []
				part_=frappe.get_doc("Apparelo Part",part)
				if part_.is_combined:
					for part_ in part_.combined_parts:
						variant_attribute_set['Part'].append(part_.parts)
				else:
					variant_attribute_set['Part'].append(part)
				variant_attribute_set['Apparelo Colour'] = self.get_attribute_values('Apparelo Colour', part)
				cutting_size = self.get_attribute_values('Apparelo Size', part)
				if self.based_on_style==1:
					style=self.get_attribute_values('Apparelo Style',part)
					variant_attribute_set['Apparelo Style'] = style
				if cutting_size:
					for apparelo_size in cutting_size:
						if apparelo_size in size:
							new_cutting_size.append(apparelo_size)
						else:
							frappe.throw(_("Size is not available"))
					variant_attribute_set['Apparelo Size'] = new_cutting_size
					variants.extend(create_variants(item+" Cut Cloth", variant_attribute_set))
					counter_attr=Counter(cutting_attribute)
					attr_set=Counter(variant_attribute_set)
					counter_attr.update(attr_set)
					cutting_attribute=dict(counter_attr)
					for value in cutting_attribute:
						cutting_attribute[value]=list(set(cutting_attribute[value]))
		else:
			frappe.throw(_("Cutting has more colours or Dia that is not available in the input"))
		return list(set(variants)),cutting_attribute

	def attribute_validate(self, attribute_name, input_attribute_values):
		if len(set(input_attribute_values))==len(set(self.get_attribute_values(attribute_name))):
			return True
		if len(set(input_attribute_values))<len(set(self.get_attribute_values(attribute_name))):
			return set(input_attribute_values).issubset(set(self.get_attribute_values(attribute_name)))
		if len(set(self.get_attribute_values(attribute_name)))<len(set(input_attribute_values)):
			return set(self.get_attribute_values(attribute_name)).issubset((set(input_attribute_values)))

	def get_matching_details(self, part, size):
		# ToDo: Part Size combination may not be unique
		dia=''
		weight=''
		count=1
		for detail in self.details:
			combined_parts=[]
			part_doc=frappe.get_doc("Apparelo Part",detail.part)
			if part_doc.is_combined:
				for part_ in part_doc.combined_parts:
					combined_parts.append(part_.parts)
				if part[0] in combined_parts:
					if detail.size == size[0]:		
						dia=detail.dia
						weight=detail.weight
						count=len(combined_parts)			
			else:
				if detail.part == part[0] and detail.size == size[0]:
					dia=detail.dia
					weight=detail.weight
		return {"Dia": dia, "Weight": weight},count

	def create_boms(self, input_item_names, variants, attribute_set, item_size,colour, piece_count, process_record, idx):
		input_items = []
		boms = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		for variant in variants:
			var=frappe.get_doc('Item', variant)
			attr = get_attr_dict(var.attributes)
			bom=create_common_bom(self, variant,attr, input_items, process_record, idx)
			boms.append(bom)
		return boms,variants

	def get_attribute_values(self, attribute_name, part=None):
		attribute_value = set()
		if attribute_name=="Apparelo Style":
			if part == None:
				for colour_mapping in self.colour_mapping:
					attribute_value.add(colour_mapping.style)
			elif part:
				for colour_mapping in self.colour_mapping:
					if colour_mapping.part == part:
						attribute_value.add(colour_mapping.style)
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
				attribute_value.add(detail.dia)
		elif attribute_name == "Apparelo Size":
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
			"item_attribute_values": []
		}).save()

	if not frappe.db.exists("Item Attribute", "Apparelo Size"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Apparelo Size",
			"item_attribute_values": []
		}).save()


@frappe.whitelist()
def get_part_size_combination(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	part_size_combination =[]
	if doc.get('details') != None:
		for item in doc.get('details'):
			if 'part' in item:
				part_size_combination.append({'part':item['part'],'size':item['size']})
	for size in doc.get('sizes'):
		for part in doc.get('parts'):
			part_size_combination.append({'part':part['parts'],'size':size['size']})
	return part_size_combination


@frappe.whitelist()
def get_part_colour_combination(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	part_colour_combination =[]
	if doc.get("based_on_style")==0:
		if doc.get('colour_mapping') != None:
			for item in doc.get('colour_mapping'):
				if 'part' in item:
					part_colour_combination.append({'part':item['part'],'colour':item['colour']})
		for colour in doc.get('colours'):
			for part in doc.get('colour_parts'):
				part_colour_combination.append({'part':part['parts'],'colour':colour['colors']})
	else:
		if doc.get('colour_mapping') != None:
			for item in doc.get('colour_mapping'):
				if 'part' in item:
					part_colour_combination.append({'part':item['part'],'colour':item['colour'],'style':item['style']})
		for colour in doc.get('colours'):
			for part in doc.get('colour_parts'):
				for style in doc.get('styles'):
					part_colour_combination.append({'part':part['parts'],'colour':colour['colors'],'style':style['styles']})
	return(part_colour_combination)

def create_common_bom(self, variant,attr, input_items, process_record, idx):
	dia_weight,count=self.get_matching_details(attr["Part"], attr["Apparelo Size"])
	attr.update(dia_weight)
	for input_item in input_items:
		input_item_attr = get_attr_dict(input_item.attributes)
		if input_item_attr["Apparelo Colour"] == attr["Apparelo Colour"]:
			if input_item_attr["Dia"][0] == attr["Dia"]:
				existing_bom = frappe.db.get_value('BOM', {'item': variant}, 'name')
				if not existing_bom:
					conversion_factor=get_conversion_factor(input_item.name,'Gram')
					bom = frappe.get_doc({
						"doctype": "BOM",
						"currency": get_default_currency(),
						"item": variant,
						"company": get_default_company(),
						"items": [
							{
								"item_code": input_item.name,
								"qty": attr["Weight"]/count,
								"uom": 'Gram',
								"conversion_factor":conversion_factor["conversion_factor"]
							}
						]
					})
					bom.save()
					bom.submit()
					return bom.name
				else:
					return existing_bom
	frappe.throw(_(f'Colour {attr["Apparelo Colour"][0]} or Dia {attr["Dia"]} entered in cutting process record {process_record} at row {idx} was not found in the input item list'))

def is_combined_parts(item):
	item_doc=frappe.get_doc("Item",item)
	for attr in item_doc.attributes:
		if attr.attribute=="Apparelo Part":
			part=attr.attribute_value
			part_=frappe.get_doc("Apparelo Part",part)
			if part_.is_combined:
				return True
			else:
				return False


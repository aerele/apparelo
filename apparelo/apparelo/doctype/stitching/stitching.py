# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from frappe import _
from frappe.model.document import Document
from six import string_types, iteritems
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants,create_additional_parts

class Stitching(Document):
	def on_submit(self):
		create_item_template(self)

	def create_variants(self, input_item_names,colour,item,final_process):
		colour.sort()
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = []
		parts = attribute_set["Part"]
		for colour_mapping in self.colour_mappings:
			for part in parts:
				if colour_mapping.part==part:
					if colour_mapping.part_colour in attribute_set["Apparelo Colour"]:
						variant_attribute_set = {}
						piece_colour=self.get_attribute_values('Apparelo Colour', part)
						piece_colour.sort()
						if "Apparelo Style" in attribute_set:
							if len(piece_colour)<len(colour):
								variant_attribute_set['Apparelo Colour']=[]
								variant_attribute_set['Apparelo Style']=[]
								for style_ in attribute_set["Apparelo Style"]:
									for color_ in piece_colour:
										if color_ in colour and style_ in colour:
											variant_attribute_set["Apparelo Style"].append(style_)
											variant_attribute_set['Apparelo Colour'].append(color_)
							else:
								if "Apparelo Style" in attribute_set:
									if attribute_set["Apparelo Style"][0] in piece_colour and piece_colour==colour:
										variant_attribute_set['Apparelo Style'] = attribute_set["Apparelo Style"]
										variant_attribute_set['Apparelo Colour'] = piece_colour
								else:
									if piece_colour==colour:
										variant_attribute_set['Apparelo Colour'] = piece_colour
									else:
										frappe.throw(_("Item colour is not available"))
						else:
							if len(piece_colour)<len(colour):
								variant_attribute_set['Apparelo Colour']=[]
								for color_ in piece_colour:
									if color_ in colour:
										variant_attribute_set['Apparelo Colour'].append(color_)
							else:
								if "Apparelo Style" in attribute_set:
									if attribute_set["Apparelo Style"][0] in piece_colour and piece_colour==colour:
										variant_attribute_set['Apparelo Style'] = attribute_set["Apparelo Style"]
										variant_attribute_set['Apparelo Colour'] = piece_colour
								else:
									if piece_colour==colour:
										variant_attribute_set['Apparelo Colour'] = piece_colour
									else:
										frappe.throw(_("Item colour is not available"))
						variant_attribute_set['Apparelo Size'] = attribute_set["Apparelo Size"]
					else:
						frappe.throw(_("Part Colour is not available in the input"))
		if final_process=="Stitching":
			if "Apparelo Style" in variant_attribute_set:
				variant_attribute_set.pop("Apparelo Style")
			variant_attribute_set.pop('Apparelo Colour')
			variants.extend(create_variants(item, variant_attribute_set))
		else:
			variants.extend(create_variants(self.item+" Stitched Cloth", variant_attribute_set))
		
		return list(set(variants))

	def validate_attribute_values(self, attribute_name, input_attribute_values):
		return set(input_attribute_values).issubset(self.get_attribute_values(attribute_name))

	def get_attribute_values(self, attribute_name, part=None):
		attribute_value = set()
		if attribute_name == "Apparelo Colour":
			if part == None:
				for colour_mapping in self.colour_mappings:
					attribute_value.add(colour_mapping.part_colour)
			elif part:
				for colour_mapping in self.colour_mappings:
					if colour_mapping.part == part:
						attribute_value.add(colour_mapping.piece_colour)
		return list(attribute_value)

	def create_boms(self, input_item_names, variants,attribute_set,item_size,colour,piece_count,final_process):
		boms = []
		for variant in variants:
			item_list = []
			for input_item in input_item_names:
				for size in attribute_set["Apparelo Size"]:
					if final_process=="Stitching":
						if size.upper() in input_item  and size.upper() in variant:
							item_list.append({"item_code": input_item,"qty":piece_count.qty ,"uom": "Nos"})
					else:
						if "Apparelo Style" in attribute_set:
							for style in attribute_set["Apparelo Style"]:
								for colour_mapping in self.colour_mappings:
									for piece_count in self.parts_per_piece:
										if style.upper() in input_item and style.upper() in variant and size.upper() in input_item  and size.upper() in variant and colour_mapping.piece_colour.upper() in variant and colour_mapping.part.upper() in input_item and colour_mapping.part_colour.upper() in input_item:
											if piece_count.part==colour_mapping.part:
												item_list.append({"item_code": input_item,"qty":piece_count.qty ,"uom": "Nos"})
						else:
							for colour_mapping in self.colour_mappings:
								for piece_count in self.parts_per_piece:
									if size.upper() in input_item  and size.upper() in variant and colour_mapping.piece_colour.upper() in variant and colour_mapping.part.upper() in input_item and colour_mapping.part_colour.upper() in input_item:
										if piece_count.part==colour_mapping.part:
											item_list.append({"item_code": input_item,"qty":piece_count.qty ,"uom": "Nos"})
			if not self.additional_parts==[]:
				# create_additional_parts(self.additional_parts_colour,self.additional_parts_size,self.additional_parts)
				for item in self.additional_parts:
						item_list.append({"item_code": item.item,"uom": "Nos","qty":item.qty})
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
		return boms

def create_item_template(self):
	if not frappe.db.exists("Item", self.item+" Stitched Cloth"):
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": self.item+" Stitched Cloth",
			"item_name": self.item+" Stitched Cloth",
			"description":self.item+" Stitched Cloth",
			"item_group": "Sub Assemblies",
			"stock_uom" : "Nos",
			"has_variants" : "1",
			"variant_based_on" : "Item Attribute",
			"is_sub_contracted_item": "1",
			"attributes" : [
				{
					"attribute" : "Apparelo Colour"
				},
				{
					"attribute" : "Apparelo Size"
				}
			]
		})
		item.save()

@frappe.whitelist()
def get_piece_colour_combination(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	piece_colour_combination =[]
	if doc.get('is_part_colour_same_as_piece_colour'):
		if doc.get('colour_mappings') != None:
			for item in doc.get('colour_mappings'):
				if 'part' in item:
					piece_colour_combination.append({'part':item['part'],'piece_colour':item['piece_colour'],'part_colour':item['part_colour']})
				else:
					break
		for colour in doc.get('piece_colours'):
			for part in doc.get('parts'):
				piece_colour_combination.append({'part':part['parts'],'piece_colour':colour['colors'],'part_colour':colour['colors']})
	else:
		if doc.get('colour_mappings') != None:
			for item in doc.get('colour_mappings'):
				if 'part' in item:
					piece_colour_combination.append({'part':item['part'],'piece_colour':item['piece_colour'],'part_colour':item['part_colour']})
				else:
					break
		for colour in doc.get('piece_colours'):
			for part in doc.get('parts'):
				piece_colour_combination.append({'part':part['parts'],'piece_colour':colour['colors'],'part_colour':' '})
	return(piece_colour_combination)

@frappe.whitelist()
def get_parts(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	parts =[]
	for part in doc.get('parts'):
		parts.append({'part':part['parts']})
	return(parts)


@frappe.whitelist()
def get_additional_item_piece_colour(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	piece_colour_combination =[]
	if doc.get('is_part_color_same_as_piece_color'):
		if doc.get('additional_parts_colour') != None:
			for item in doc.get('additional_parts_colour'):
				if 'item' in item:
					piece_colour_combination.append({'item':item['item'],'piece_colour':item['piece_colour'],'part_colour':item['part_colour']})
				else:
					break
		for colour in doc.get('piece_colors'):
			for item in doc.get('items'):
				piece_colour_combination.append({'item':item['items'],'piece_colour':colour['colors'],'part_colour':colour['colors']})
	else:
		if doc.get('additional_parts_colour') != None:
			for item in doc.get('additional_parts_colour'):
				if 'item' in item:
					piece_colour_combination.append({'item':item['item'],'piece_colour':item['piece_colour'],'part_colour':item['part_colour']})
				else:
					break
		for colour in doc.get('piece_colors'):
			for item in doc.get('items'):
				piece_colour_combination.append({'item':item['items'],'piece_colour':colour['colors'],'part_colour':' '})
	return(piece_colour_combination)

@frappe.whitelist()
def get_items(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	items =[]
	for item in doc.get('items'):
		items.append({'item':item['items']})
	return(items)

@frappe.whitelist()
def get_additional_item_size(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	size_combination =[]
	if doc.get('is_part_size_same_as_piece_size'):
		if doc.get('additional_parts_size') != None:
			for item in doc.get('additional_parts_size'):
				if 'item' in item:
					size_combination.append({'item':item['item'],'piece_size':item['piece_size'],'part_size':item['part_size']})
				else:
					break
		for size in doc.get('piece_sizes'):
			for item in doc.get('additional_items'):
				size_combination.append({'item':item['items'],'piece_size':size['size'],'part_size':size['size']})
	else:
		if doc.get('additional_parts_size') != None:
			for item in doc.get('additional_parts_size'):
				if 'item' in item:
					size_combination.append({'item':item['item'],'piece_size':item['piece_size'],'part_size':item['part_size']})
				else:
					break
		for size in doc.get('piece_sizes'):
			for item in doc.get('additional_items'):
				size_combination.append({'item':item['items'],'piece_size':size['size'],'part_size':' '})
	return(size_combination)
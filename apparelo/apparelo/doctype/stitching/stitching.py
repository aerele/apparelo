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
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants,create_additional_parts,matching_additional_part
from apparelo.apparelo.utils.utils import validate_additional_parts_mapping, validate_table_fields

class Stitching(Document):
	def on_submit(self):
		result, value = validate_table_fields(self.parts_per_piece, self.colour_mappings, 'Stitching')
		if not result:
			frappe.throw(_(f'The part {value} entered in parts per piece table was not found in colour mappings table.'))
		result, value = validate_table_fields(self.colour_mappings, self.parts_per_piece, 'Stitching')
		if not result:
			frappe.throw(_(f'The part {value} entered in colour mappings table was not found in parts per piece table.'))
		if self.enable_additional_parts:
			validate_additional_parts_mapping(self.additional_parts, self.additional_parts_size, self.additional_parts_colour)

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
		if self.enable_set_item:
			variant_attribute_set['Part'] = [self.part]
		if final_process=="Stitching":
			if "Apparelo Style" in variant_attribute_set:
				variant_attribute_set.pop("Apparelo Style")
			variant_attribute_set.pop('Apparelo Colour')
			variants.extend(create_variants(item, variant_attribute_set))
		else:
			variants.extend(create_variants(item+" Stitched Cloth", variant_attribute_set))
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
		if self.enable_additional_parts:
			additional_parts=create_additional_parts(self.additional_parts_colour,self.additional_parts_size,self.additional_parts)
		for variant in variants:
			item_list = []
			variant_doc=frappe.get_doc("Item",variant)
			variant_attr = get_attr_dict(variant_doc.attributes)
			for input_item in input_item_names:
				input_item_doc=frappe.get_doc("Item",input_item)
				input_attr = get_attr_dict(input_item_doc.attributes)
				for size in attribute_set["Apparelo Size"]:
					if final_process=="Stitching":
						if size in input_attr["Apparelo Size"]  and size in variant_attr["Apparelo Size"]:
							item_list.append({"item_code": input_item,"qty":piece_count.qty ,"uom": "Nos"})
					else:
						if "Apparelo Style" in attribute_set and "Apparelo Style" in input_attr:
							for style in attribute_set["Apparelo Style"]:
								for colour_mapping in self.colour_mappings:
									for piece_count in self.parts_per_piece:
										if style in input_attr["Apparelo Style"] and style in variant_attr["Apparelo Colour"] and size in input_attr["Apparelo Size"]  and size in variant_attr["Apparelo Size"] and colour_mapping.piece_colour in variant_attr["Apparelo Colour"] and colour_mapping.part in input_attr["Part"] and colour_mapping.part_colour in input_attr["Apparelo Colour"]:
											if piece_count.part==colour_mapping.part:
												item_list.append({"item_code": input_item,"qty":piece_count.qty ,"uom": "Nos"})
						else:
							for colour_mapping in self.colour_mappings:
								for piece_count in self.parts_per_piece:
									if size in input_attr["Apparelo Size"]  and size in variant_attr["Apparelo Size"] and colour_mapping.piece_colour in variant_attr["Apparelo Colour"] and colour_mapping.part in input_attr["Part"] and colour_mapping.part_colour in input_attr["Apparelo Colour"]:
										if piece_count.part==colour_mapping.part:
											item_list.append({"item_code": input_item,"qty":piece_count.qty ,"uom": "Nos"})
			if self.enable_additional_parts:
				matched_part=matching_additional_part(additional_parts,self.additional_parts_colour,self.additional_parts_size,self.additional_parts,variant)
				for additional_part in self.additional_parts:
					if additional_part.based_on=="None":
						item_list.append({"item_code": additional_part.item,"qty":additional_part.qty ,"uom": additional_part.uom})
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
		return boms

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
			for item in doc.get('color_additional_items'):
				piece_colour_combination.append({'item':item['items'],'piece_colour':colour['colors'],'part_colour':colour['colors']})
	else:
		if doc.get('additional_parts_colour') != None:
			for item in doc.get('additional_parts_colour'):
				if 'item' in item:
					piece_colour_combination.append({'item':item['item'],'piece_colour':item['piece_colour'],'part_colour':item['part_colour']})
				else:
					break
		for colour in doc.get('piece_colors'):
			for item in doc.get('color_additional_items'):
				piece_colour_combination.append({'item':item['items'],'piece_colour':colour['colors'],'part_colour':' '})
	return(piece_colour_combination)

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
			for item in doc.get('size_additional_items'):
				size_combination.append({'item':item['items'],'piece_size':size['size'],'part_size':size['size']})
	else:
		if doc.get('additional_parts_size') != None:
			for item in doc.get('additional_parts_size'):
				if 'item' in item:
					size_combination.append({'item':item['item'],'piece_size':item['piece_size'],'part_size':item['part_size']})
				else:
					break
		for size in doc.get('piece_sizes'):
			for item in doc.get('size_additional_items'):
				size_combination.append({'item':item['items'],'piece_size':size['size'],'part_size':' '})
	return(size_combination)
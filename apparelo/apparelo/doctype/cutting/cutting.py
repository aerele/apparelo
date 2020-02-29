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

class Cutting(Document):
	def on_submit(self):
		create_item_attribute()
		create_item_template(self)

	def create_variants(self, input_item_names,size):
		cutting_attribute={}
		input_items = []
		for input_item_name in set(input_item_names):
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = []
		if self.attribute_validate("Apparelo Colour", attribute_set["Apparelo Colour"]) and self.attribute_validate("Dia", attribute_set["Dia"]):
			parts = set(self.get_attribute_values("Part"))
			variant_attribute_set = {}
			for part in parts:
				variant_attribute_set['Part'] = []
				part_=frappe.get_doc("Apparelo Part",part)
				if part_.is_combined:
					for part_ in part_.combined_parts:
						variant_attribute_set['Part'].append(part_.parts)
				else:
					variant_attribute_set['Part'].append(part)
				variant_attribute_set['Apparelo Colour'] = self.get_attribute_values('Apparelo Colour', part)
				cutting_size=self.get_attribute_values('Apparelo Size', part)
				if self.based_on_style==1:
					style=self.get_attribute_values('Apparelo Style',part)
					variant_attribute_set['Apparelo Style'] = style
				size.sort()
				cutting_size.sort()
				if cutting_size==size:
					variant_attribute_set['Apparelo Size'] = cutting_size
					variants.extend(create_variants(self.item+" Cut Cloth", variant_attribute_set))
					counter_attr=Counter(cutting_attribute)
					attr_set=Counter(variant_attribute_set)
					counter_attr.update(attr_set)
					cutting_attribute=dict(counter_attr)
					for value in cutting_attribute:
						cutting_attribute[value]=list(set(cutting_attribute[value]))
				else:
					frappe.throw(_("Size is not available"))
		else:
			frappe.throw(_("Cutting has more colours or Dia that is not available in the input"))
		print(list(set(variants)),cutting_attribute)
		return list(set(variants)),cutting_attribute

	def attribute_validate(self, attribute_name, input_attribute_values):
		if len(set(input_attribute_values))==len(set(self.get_attribute_values(attribute_name))):
			return True
		if len(set(input_attribute_values))<len(set(self.get_attribute_values(attribute_name))):
			return set(input_attribute_values).issubset(set(self.get_attribute_values(attribute_name)))
		if len(set(self.get_attribute_values(attribute_name)))<len(set(input_attribute_values)):
			return set(self.get_attribute_values(attribute_name)).issubset((set(input_attribute_values)))

	def get_matching_details(self, part, size):
		combined_parts=[]
		# ToDo: Part Size combination may not be unique
		for detail in self.details:
			part_doc=frappe.get_doc("Apparelo Part",detail.part)
			if part_doc.is_combined:
				for part_ in part_.combined_parts:
					combined_parts.append(part_.parts)
				if part in combined_parts:
					if detail.size == size[0]:
						return {"Dia": detail.dia, "Weight": detail.weight},count
			else:
				if detail.part == part[0] and detail.size == size[0]:
					return {"Dia": detail.dia, "Weight": detail.weight},count

	def create_boms(self, input_item_names, variants, attribute_set,item_size,colour,piece_count):
		input_items = []
		# combo_=[]
		boms = []
		# variant_=[]
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		# for part in attribute_set["Part"]:
		# 	part_=frappe.get_doc("Apparelo Part",part)
		# 	if part_.is_combined:
		# 		# combined_part={}
		# 		# variant=[]
		# 		# combined_part['color']=attribute_set["Apparelo Colour"]
		# 		# combined_part['Size']=attribute_set["Apparelo Size"]
		# 		# combined_part['Part']=part
		# 		count=len(part_.combined_parts)
		# 		# combined_part['count']=count
		# 		# for variant in variants:
		# 		# 	var=frappe.get_doc('Item', variant)
		# 		# 	attr = get_attr_dict(var.attributes)
		# 		# 	if part in attr['Part']:
		# 		# 		variant_.append(input)
		# 		# 		bom=create_common_bom(self,variant,attr,input_items)
		# 		# combined_part['variants']=variant_
		# 		# combo_.append(combined_part)
		# # print(combo_,"PPP")
		# # ff
		for variant in variants:
			var=frappe.get_doc('Item', variant)
			attr = get_attr_dict(var.attributes)
			# if combo_:
				# for combo in combo_:
			# if is_combined_parts(variant):
			# # if len(attr['Part'][0])<len(combo['Part']) and attr['Part'][0] in combo['Part']:
			# 	combined_parts=[]
			# 	part_doc=frappe.get_doc("Apparelo Part",detail.part)
			# 	if part_doc.is_combined:
			# 		for part_ in part_.combined_parts:
			# 			combined_parts.append(part_.parts)
			# 	attr["Part"]=combined_parts
			# 	combo_bom=create_common_bom(self,variant,attr,input_items,count)
			# 	# combo,input_items,variant
			# 	boms.append(combo_bom)
			# else:
				# if not is_combined_parts(variant):
			bom=create_common_bom(self,variant,attr,input_items)
			boms.append(bom)
			# else:
			# 	if not is_combined_parts(variant):
			# 		bom_=create_common_bom(self,variant,attr,input_items,count)
			# 		boms.append(bom_)
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

def create_item_template(self):
	if self.based_on_style==0:
		if not frappe.db.exists("Item", self.item+" Cut Cloth"):
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": self.item+" Cut Cloth",
				"item_name": self.item+" Cut Cloth",
				"description":self.item+" Cut Cloth",
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
						"attribute" : "Part"
					},
					{
						"attribute" : "Apparelo Size"
					}
				]
			})
			item.save()
	else:
		if not frappe.db.exists("Item", self.item+" Cut Cloth"):
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": self.item+" Cut Cloth",
				"item_name": self.item+" Cut Cloth",
				"description":self.item+" Cut Cloth",
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
						"attribute" : "Part"
					},
					{
						"attribute" : "Apparelo Size"
					},
					{
						"attribute" : "Apparelo Style"
					}
				]
			})
			item.save()


@frappe.whitelist()
def get_part_size_combination(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	part_size_combination =[]
	if doc.get('details') != None:
		for item in doc.get('details'):
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
				part_colour_combination.append({'part':item['part'],'colour':item['colour']})
		for colour in doc.get('colours'):
			for part in doc.get('colour_parts'):
				part_colour_combination.append({'part':part['parts'],'colour':colour['colors']})
	else:
		if doc.get('colour_mapping') != None:
			for item in doc.get('colour_mapping'):
				part_colour_combination.append({'part':item['part'],'colour':item['colour'],'style':item['style']})
		for colour in doc.get('colours'):
			for part in doc.get('colour_parts'):
				for style in doc.get('styles'):
					part_colour_combination.append({'part':part['parts'],'colour':colour['colors'],'style':style['styles']})
	return(part_colour_combination)

# def create_combined_bom(self,variant,attr,input_items,combo):
# 	# combo,input,input_item,
# 	weight=1
# 	# attr.update(self.get_matching_details(attr["Part"], attr["Apparelo Size"]))
# 	for input_item in input_items:
# 		input_item_attr = get_attr_dict(input_item.attributes)
# 		print(input_item_attr["Apparelo Colour"],attr["Apparelo Colour"])
# 		if input_item_attr["Apparelo Colour"] == attr["Apparelo Colour"]:
# 			if input_item_attr["Dia"][0] == attr["Dia"]:
# 				existing_bom = frappe.db.get_value('BOM', {'item': variant}, 'name')
# 				if not existing_bom:
# 					conversion_factor=get_conversion_factor(input_item.name,'Gram')
# 					bom = frappe.get_doc({
# 						"doctype": "BOM",
# 						"currency": get_default_currency(),
# 						"item": variant,
# 						"company": get_default_company(),
# 						"items": [
# 							{
# 								"item_code": input_item.name,
# 								"qty": weight/combo['count'],
# 								"uom": 'Gram',
# 								"conversion_factor":conversion_factor["conversion_factor"]
# 							}
# 						]
# 					})
# 					bom.save()
# 					bom.submit()
# 					print(input_item.name,bom.name)
# 					return bom.name
# 				else:
# 					return existing_bom
# 	frappe.throw(_('Colour entered in cutting process was not found in IPD colour list.'))
	# item_doc=frappe.get_doc("Item",input_item)
	# print(input)
	# for variant in input:
	# 	item_ = get_attr_dict(item_doc.attributes)
	# 	variant_doc=frappe.get_doc("Item",variant.name)
	# 	variant_attr = get_attr_dict(variant_doc.attributes)
	# 	if item_["Apparelo Colour"][0] in combo["color"] and item_["Apparelo Size"][0] in combo["Size"]:
	# 		if item_["Apparelo Colour"][0] in variant_attr["Apparelo Colour"] and item_["Apparelo Size"][0] in variant_attr["Apparelo Size"]:
	# 			existing_bom = frappe.db.get_value('BOM', {'item':input_item}, 'name')
	# 			if not existing_bom:
	# 				bom = frappe.get_doc({
	# 					"doctype": "BOM",
	# 					"currency": get_default_currency(),
	# 					"item": input_item,
	# 					"company": get_default_company(),
	# 					"quantity": 1,
	# 					"uom": 'Combined Part',
	# 					"items": [
	# 						{
	# 							"item_code": variant.name,
	# 							"qty": weight/combo['count'],
	# 							"uom": 'Combined Part',
	# 							"stock_qty":weight/combo['count'],
	# 							"stock_uom":'Combined Part'
	# 						}
	# 					]
	# 				})
	# 				bom.save()
	# 				bom.submit()
	# 				print(variant,bom.name)
	# 				return bom.name
	# 			else:
	# 				return existing_bom

def create_common_bom(self,variant,attr,input_items):
	print(attr)
	self.get_matching_details(attr["Part"], attr["Apparelo Size"])
	attr.update()
	for input_item in input_items:
		input_item_attr = get_attr_dict(input_item.attributes)
		print(input_item_attr["Apparelo Colour"],attr["Apparelo Colour"])
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
					print(input_item.name,bom.name)
					return bom.name
				else:
					return existing_bom
	frappe.throw(_('Colour entered in cutting process was not found in IPD colour list.'))

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


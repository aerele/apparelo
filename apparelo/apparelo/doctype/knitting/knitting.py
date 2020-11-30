# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from apparelo.apparelo.utils.utils import is_similar_bom
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants
import hashlib

class Knitting(Document):
	def on_submit(self):
		create_item_template()
		create_item_attribute()

	def create_variants(self, input_item_names):
		input_items = []
		new_variants=[]
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		attribute_set.update(self.get_variant_values())
		variants = create_variants('Knitted Cloth', attribute_set)
		for variant in variants:
			variant_doc=frappe.get_doc("Item",variant)
			variant_attr = get_attr_dict(variant_doc.attributes)
			for dia in attribute_set["Dia"]:
				if dia in variant_attr['Dia']:
					if not dia+" Dia" in variant:
						hash_=hashlib.sha256(variant.replace('Knitted Cloth',"").encode()).hexdigest()
						if variant_attr['Yarn Shade'][0]=='Plain':
							new_variant='Knitted Cloth-'+variant_attr['Yarn Category'][0].upper()+'-'+variant_attr['Dia'][0]+' Dia'+'-'+variant_attr['Knitting Type'][0].upper()
						else:
							new_variant='Knitted Cloth-'+variant_attr['Yarn Shade'][0].upper()+'-'+variant_attr['Yarn Category'][0].upper()+'-'+variant_attr['Dia'][0]+' Dia'+'-'+variant_attr['Knitting Type'][0].upper()
						doc=frappe.get_doc("Item",variant)
						doc.print_code=new_variant
						doc.save()
						new_variant=new_variant+" "+hash_[0:7]
						r_variant=frappe.rename_doc("Item",variant,new_variant)
						new_variants.append(r_variant)
					else:
						new_variants.append(variant)
		if len(new_variants)==0:
			new_variants=variants
		return new_variants

	def create_boms(self, input_item_names, variants,attribute_set,item_size,colour,piece_count):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		boms = []
		doc_values = self.get_variant_values()
		for item in input_items:
			attr = get_attr_dict(item.attributes)
			attr.update(doc_values)
			args_set = generate_keyed_value_combinations(attr)
			for attribute_values in args_set:
				variant = get_variant("Knitted Cloth", args=attribute_values)
				if variant in variants:
					bom_for_variant = frappe.get_doc({
						"doctype": "BOM",
						"currency": get_default_currency(),
						"item": variant,
						"company": get_default_company(),
						"quantity": self.output_qty,
						"uom": self.output_uom,
						"items": [
							{
								"item_code": item.name,
								"qty": self.input_qty,
								"uom": self.input_uom,
								"rate": 0.0,
							}
						]
					})
					existing_bom_name = frappe.db.get_value('BOM', {'item': variant, 'docstatus': 1, 'is_active': 1}, 'name')
					if not existing_bom_name:
						bom_for_variant.save()
						bom_for_variant.submit()
						boms.append(bom_for_variant.name)
					else:
						existing_bom = frappe.get_doc('BOM', existing_bom_name)
						similar_diff = is_similar_bom(existing_bom, bom_for_variant)
						if similar_diff:
							boms.append(existing_bom_name)
						else:
							frappe.throw(_("Active BOM with different Materials or qty already exists for the item {0}. Please make this BOM {1} inactive and try again.").format(variant, """<a href="#Form/BOM/{0}">{1}</a>""".format(existing_bom_name, existing_bom_name)))
				else:
					frappe.throw(_("Unexpected error while creating BOM. Expected variant not found in list of supplied variants"))
		return boms

	def get_variant_values(self):
		attribute_set = {}
		attribute_set['Knitting Type'] = [self.type]
		variant_dia = []
		for dia in self.dia:
			variant_dia.append(dia.dia)
		attribute_set['Dia'] = variant_dia
		return attribute_set

def create_item_attribute():
	if not frappe.db.exists("Item Attribute", "Yarn Shade"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Yarn Shade",
			"item_attribute_values": [
				{
					"attribute_value" : "Plain",
					"abbr" : "Plain"
				},
				{
					"attribute_value" : "A.Melange",
					"abbr" : "A.Melange"
				},
				{
					"attribute_value" : "G.Melange",
					"abbr" : "G.Melange"
				}
			]
		}).save()

	if not frappe.db.exists("Item Attribute", "Yarn Category"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Yarn Category",
			"item_attribute_values": [
				{
					"attribute_value" : "Green Label",
					"abbr" : "Green Label"
				},
				{
					"attribute_value" : "Violet Label",
					"abbr" : "Violet Label"
				},
				{
					"attribute_value" : "Red Label",
					"abbr" : "Red Label"
				}
			]
		}).save()

	if not frappe.db.exists("Item Attribute", "Yarn Count"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Yarn Count",
			"item_attribute_values": [
				{
					"attribute_value" : "30'S",
					"abbr" : "30'S"
				},
				{
					"attribute_value" : "34'S",
					"abbr" : "34'S"
				},
				{
					"attribute_value" : "36'S",
					"abbr" : "36'S"
				},
				{
					"attribute_value" : "40'S",
					"abbr" : "40'S"
				}
			]
		}).save()

	if not frappe.db.exists("Item Attribute", "Knitting Type"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Knitting Type",
			"item_attribute_values": []
		}).save()

def create_item_template():
	if not frappe.db.exists("Item", "Yarn"):
		frappe.get_doc({
			"doctype": "Item",
			"item_code": "Yarn",
			"item_name": "Yarn",
			"description": "Yarn",
			"item_group": "Raw Material",
			"stock_uom" : "Kg",
			"has_variants" : "1",
			"variant_based_on" : "Item Attribute",
			"attributes" : [
				{
					"attribute" : "Yarn Shade"
				},
				{
					"attribute" : "Yarn Category"
				},
				{
					"attribute" : "Yarn Count"
				}
			]
		}).save()

	if not frappe.db.exists("Item", "Knitted Cloth"):
		frappe.get_doc({
			"doctype": "Item",
			"item_code": "Knitted Cloth",
			"item_name": "Knitted Cloth",
			"description": "Knitted Cloth",
			"item_group": "Sub Assemblies",
			"stock_uom" : "Kg",
			"has_variants" : "1",
			"variant_based_on" : "Item Attribute",
			"is_sub_contracted_item": "1",
			"attributes" : [
				{
					"attribute" : "Yarn Shade"
				},
				{
					"attribute" : "Yarn Category"
				},
				{
					"attribute" : "Yarn Count"
				},
				{
					"attribute" : "Dia"
				},
				{
					"attribute" : "Knitting Type"
				}
			]
		}).save()
def create_attr_values():
	colour=["Red","Blue","Green","Black","Navy","A.Mel","G.Mel","Grey","Brown","Maroon","magenta"]
	part=["Front","Back","Panel","Sleeve","Folding","Net Folding"]
	Knitting_type=["Single Rib","Fine","Single Rib (Fold)","Fine (Fold)"]
	for attribute_ in Knitting_type:
		existing_doc=frappe.db.get_value('Knitting Type', {'type': attribute_}, 'name')
		if not existing_doc:
			type_doc=frappe.new_doc("Knitting Type")
			type_doc.type=attribute_
			type_doc.save()
	for attribute_ in colour:
		existing_doc=frappe.db.get_value('Apparelo Colour', {'colour': attribute_}, 'name')
		if not existing_doc:
			color_doc=frappe.new_doc("Apparelo Colour")
			color_doc.colour=attribute_
			color_doc.save()
	for attribute_ in part:
		existing_doc=frappe.db.get_value('Apparelo Part', {'part_name': attribute_}, 'name')
		if not existing_doc:
			part_doc=frappe.new_doc("Apparelo Part")
			part_doc.part_name=attribute_
			part_doc.save()
	for num in range(35,120,5):
		existing_doc=frappe.db.get_value('Apparelo Size', {'size': str(num) +" cm"}, 'name')
		if not existing_doc:
			size_doc=frappe.new_doc("Apparelo Size")
			size_doc.size= str(num) +" cm"
			size_doc.save()
def create_additional_attribute():
	if not frappe.db.exists("Item Attribute", "Print Type"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Print Type",
			"item_attribute_values": []
		}).save()
	print_type=["Plain","Roll Printing"]
	for attribute_ in print_type:
		existing_doc=frappe.db.get_value('Print Type', {'type': attribute_}, 'name')
		if not existing_doc:
			type_doc=frappe.new_doc("Print Type")
			type_doc.type=attribute_
			type_doc.save()
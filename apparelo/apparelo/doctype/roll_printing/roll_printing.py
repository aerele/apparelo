# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
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

class RollPrinting(Document):
	def on_submit(self):
		create_item_template()
		create_item_attribute()
	def create_variants(self, input_item_names, colour=None, item=None, final_process=None):
		new_variants=[]
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes,input_items)))
		attribute_set.update(self.get_variant_values())
		variants = create_variants('Roll Printed cloth', attribute_set)
		for variant in variants:
			variant_doc=frappe.get_doc("Item",variant)
			variant_attr = get_attr_dict(variant_doc.attributes)
			for dia in attribute_set["Dia"]:
				if dia in variant_attr['Dia']:
					if not dia+" Dia" in variant:
						hash_=hashlib.sha256(variant.replace('Roll Printed cloth',"").encode()).hexdigest()
						new_variant=variant.replace(dia,dia+" Dia")
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

	def create_boms(self, input_item_names, variants, colour, attribute_set=None, item_size=None, piece_count=None, final_item=None, final_process=None):
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
				variant = get_variant('Roll Printed cloth',args=attribute_values)
				if variant in variants:
					bom_for_variant = frappe.get_doc({
						"doctype": "BOM",
						"currency": get_default_currency(),
						"item": variant,
						"company": get_default_company(),
						"quantity": 1,
						"uom": "Kg",
						"items": [
							{
								"item_code": item.name,
								"qty": 1,
								"uom": "Kg",
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
		print_type = []
		print_type.append(self.print_type)
		attribute_set['Print Type'] = print_type
		return attribute_set

def create_item_attribute():
	if not frappe.db.exists("Item Attribute", "Print Type"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Print Type",
			"item_attribute_values": []
		}).save()
def create_item_template():
	if not frappe.db.exists('Item','Roll Printed Cloth'):
		frappe.get_doc({
			"doctype": "Item",
			"item_code": "Roll Printed Cloth",
			"item_name": "Roll Printed Cloth",
			"description": "Roll Printed Cloth",
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
				},
				{
					"attribute" : "Apparelo Colour"
				},
				{
					"attribute" : "Print Type"
				}
			]
		}).save()

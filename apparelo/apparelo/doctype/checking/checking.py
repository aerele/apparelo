# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants

class Checking(Document):
	def create_variants(self, input_item_names, colour=None, item=None, final_process=None):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		if self.enable_set_item:
			attribute_set['Part'] = [self.part]
		if final_process=="Checking":
			attribute_set.pop("Apparelo Colour")
			variants = create_variants(item, attribute_set)
		else:
			variants = create_variants(item+" Checked Cloth", attribute_set)
		return variants

	def create_boms(self, input_item_names, variants, colours, attribute_set=None, item_size=None, piece_count=None, final_item=None, final_process=None):
		
		boms = []
		for variant in variants:
			item_list = []
			variant_doc=frappe.get_doc("Item",variant)
			variant_attr = get_attr_dict(variant_doc.attributes)
			for input_item in input_item_names:
				input_item_doc=frappe.get_doc("Item",input_item)
				input_attr = get_attr_dict(input_item_doc.attributes)
				for size in item_size:
					if final_process=="Checking":
						if size in input_attr["Apparelo Size"]  and size in variant_attr["Apparelo Size"]:
							item_list.append({"item_code": input_item,"uom": "Nos"})
					else:
						for colour in colours:
							if size in input_attr["Apparelo Size"]  and size in variant_attr["Apparelo Size"] and colour in input_attr["Apparelo Colour"] and colour in variant_attr["Apparelo Colour"]:
								item_list.append({"item_code": input_item,"uom": "Nos"})
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

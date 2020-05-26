# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext import get_default_company, get_default_currency
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant
from apparelo.apparelo.utils.item_utils import get_attr_dict, get_item_attribute_set, create_variants

class PiecePrinting(Document):

	def create_variants(self, input_item_names, item):
		input_items = []
		for input_item_name in input_item_names:
			input_item_name_doc=frappe.get_doc("Item",input_item_name)
			input_item_name_attr = get_attr_dict(input_item_name_doc.attributes)
			if self.part in input_item_name_attr['Part']:
				input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		variants = []
		variants.extend(create_variants(item+" Printed Cloth", attribute_set))
		return variants

	def create_boms(self, input_item_names, variants, attribute_set,item_size,colour_list,piece_count):
		boms = []
		input_item_list = []
		for variant in variants:
			variant_doc=frappe.get_doc("Item",variant)
			variant_attr = get_attr_dict(variant_doc.attributes)
			item_list = []
			for input_item in input_item_names:
				input_item_doc=frappe.get_doc("Item",input_item)
				input_attr = get_attr_dict(input_item_doc.attributes)
				for size in item_size:
					for colour in colour_list:
						if not ('Apparelo Style' in input_attr and 'Apparelo Style' in variant_attr):
							if size in input_attr["Apparelo Size"]  and size in variant_attr["Apparelo Size"] and colour in input_attr["Apparelo Colour"] and colour in variant_attr["Apparelo Colour"] and self.part in variant_attr["Part"] and self.part in input_attr["Part"]:
								input_item_list.append(input_item)
								item_list.append({"item_code": input_item,"uom": "Nos"})
						else:
							if size in input_attr["Apparelo Size"]  and size in variant_attr["Apparelo Size"] and colour in input_attr["Apparelo Style"] and colour in variant_attr["Apparelo Style"] and self.part in variant_attr["Part"] and self.part in input_attr["Part"]:
								input_item_list.append(input_item)
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
		return boms, input_item_list

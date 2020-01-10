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
from itertools import combinations

class Packing(Document):
	def on_submit(self):
		create_item_template(self)

	def create_variants(self, input_item_names,item):
		input_items = []
		for input_item_name in input_item_names:
			input_items.append(frappe.get_doc('Item', input_item_name))
		attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, input_items)))
		piece_count=len(attribute_set["Apparelo Colour"])
		attribute_set.pop('Apparelo Colour')
		variants=create_variants(item, attribute_set)
		return list(set(variants)),piece_count

	def create_boms(self, input_item_names, variants, attribute_set,item_size,colour,piece_count):
		print("&&&&&&",input_item_names,"$$$$")
		boms = []
		if piece_count==self.input_qty:
			for variant in variants:
				item_list = []
				for input_item in input_item_names:
					for size in item_size:
						if size.upper() in input_item  and size.upper() in variant:
							item_list.append({"item_code": input_item,"uom": "Nos"})
				for item in self.additional_part:
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
		if self.input_qty > piece_count:
			frappe.throw(_("Input Quantity is not available in Packing"))
		if self.input_qty < piece_count:
			print("232")
			for size in item_size:
				for items in input_item_names:
					items_=[]
					if size.upper() in items:
						print("111")
						items_.extend(items)
				print("ASD",items_,"ASDF")
				combo=list(combinations(items_,self.input_qty))
				print("indhu",self.input_qty,"indhu")
				print("SDFG",combo,"QWER")
				for variant in variants:
					print("2407")
					for combo_ in combo:
						print("1912")
						item_list_=[]
						for item_ in combo_:
							print("1306")
							for size in item_size:
								print("1233",variants,"1233",item_,"1232")
								if size.upper() in item_  and size.upper() in variant:
									print("#$%",item_,"@#@")
									item_list_.append({"item_code": item_,"uom": "Nos"})
						for item in self.additional_part:
								item_list_.append({"item_code": item.item,"uom": "Nos","qty":item.qty})
						print("$$$$$",item_list_,"$$$$$$")
						bom = frappe.get_doc({
							"doctype": "BOM",
							"currency": get_default_currency(), 
							"uom": "Nos",
							"is_default":0,
							"is_active":1,
							"item": variant,
							"company": get_default_company(),
							"items": item_list_
						})
						bom.save()
						bom.submit()
						boms.append(bom.name)
						print(bom.name)
		return boms


def create_item_template(self):
	if not frappe.db.exists("Item",self.item+" Packed Cloth"):
		frappe.get_doc({
		"doctype": "Item",
		"item_code": self.item+" Packed Cloth",
		"item_name": self.item+" Packed Cloth",
		"description":self.item+" Packed Cloth",
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
	}).save()

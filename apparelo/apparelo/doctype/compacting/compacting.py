# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
class Compacting(Document):
	def on_submit(self):
		create_item_template()

def create_item_template():
	if not frappe.db.exists("Item Attribute", "From Dia"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "From Dia",
			"numeric_values": 1,
			"from_range": 18.0,
			"to_range": 36.0,
			"increment": 0.25
		}).save()
	if not frappe.db.exists("Item Attribute", "To Dia"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "To Dia",
			"numeric_values": 1,
			"from_range": 18.0,
			"to_range": 36.0,
			"increment": 0.25
		}).save()
	# if not frappe.db.exists("Item Attribute", "Target GSM"):
	# 	frappe.get_doc({
	# 		"doctype": "Item Attribute",
	# 		"attribute_name": "Target GSM",
	# 		"numeric_values": 1,
	# 		"from_range": 120,
	# 		"to_range": 180,
	# 		"increment": 1
	# 	}).save()
	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Compacted Cloth",
		"item_name": "Compacteded Cloth",
		"description": "Compaced Cloth",
		"item_group": "Sub Assemblies",
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
			},
			{
				"attribute" : "Dia" 
			},
			{
				"attribute" : "Knitting Type"
			},
			{
				"attribute" : "Apparelo Colour" 
			}
		]
	})
	item.save()
	item.submit()

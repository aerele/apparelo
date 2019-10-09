# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Knitting(Document):
	def on_submit(self):
		create_item_template()

def create_item_template():
	if not frappe.db.exists("Item Attribute", "Yarn Shade"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Yarn Shade",
			"item_attribute_values": [
				{
					"attribute_value" : "Grey",
					"abbr" : "Grey"
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

	if not frappe.db.exists("Item Attribute", "Dia"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Dia",
			"numeric_values": 1,
			"from_range": 18.0,
			"to_range": 36.0,
			"increment": 0.25
		}).save()
	if not frappe.db.exists("Item Attribute", "Knitting Type"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Knitting Type",
			"item_attribute_values": [
				{
					"attribute_value" : "Single Rib",
					"abbr" : "Single Rib"
				},
				{
					"attribute_value" : "Fine",
					"abbr" : "Fine"
				},
				{
					"attribute_value" : "Single Rib (Fold)",
					"abbr" : "Single Rib (Fold)"
				},
				{
					"attribute_value" : "Fine (Fold)",
					"abbr" : "Fine (Fold)"
				}
			]
		}).save()

	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Yarn",
		"item_name": "Yarn",
		"description": "Yarn",
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
			}
		]
	})
	item.save()
	item.submit()
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Knitted Cloth",
		"item_name": "Knitted Cloth",
		"description": "Knitted Cloth",
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
			}
		]
	})
	item.save()
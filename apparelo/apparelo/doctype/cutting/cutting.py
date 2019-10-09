# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Cutting(Document):
	def on_submit(self):
		create_item_attribute()
		create_item_template()

def create_item_attribute():
	if not frappe.db.exists("Item Attribute", "Part"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Part",
			"item_attribute_values": [
				{
					"attribute_value" : "Front",
					"abbr" : "Front"
				},
				{
					"attribute_value" : "Back",
					"abbr" : "Back"
				},
				{
					"attribute_value" : "Panel",
					"abbr" : "Panel"
				},
				{
					"attribute_value" : "Sleeve",
					"abbr" : "Sleeve"
				}
			]
		}).save()
	if not frappe.db.exists("Item Attribute", "Apparelo Size"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Apparelo Size",
			"item_attribute_values": [
				{
					"attribute_value" : "35 cm",
					"abbr" : "35 cm"
				},
				{
					"attribute_value" : "40 cm",
					"abbr" : "40 cm"
				},
				{
					"attribute_value" : "45 cm",
					"abbr" : "45 cm"
				},
				{
					"attribute_value" : "50 cm",
					"abbr" : "50 cm"
				},
				{
					"attribute_value" : "55 cm",
					"abbr" : "55 cm"
				},
				{
					"attribute_value" : "60 cm",
					"abbr" : "60 cm"
				},
				{
					"attribute_value" : "65 cm",
					"abbr" : "65 cm"
				},
				{
					"attribute_value" : "70 cm",
					"abbr" : "70 cm"
				},
				{
					"attribute_value" : "75 cm",
					"abbr" : "75 cm"
				},
				{
					"attribute_value" : "80 cm",
					"abbr" : "80 cm"
				},
				{
					"attribute_value" : "85 cm",
					"abbr" : "85 cm"
				},
				{
					"attribute_value" : "90 cm",
					"abbr" : "90 cm"
				},
				{
					"attribute_value" : "95 cm",
					"abbr" : "95 cm"
				},
				{
					"attribute_value" : "100 cm",
					"abbr" : "100 cm"
				},
				{
					"attribute_value" : "105 cm",
					"abbr" : "105 cm"
				},
				{
					"attribute_value" : "110 cm",
					"abbr" : "110 cm"
				},
				{
					"attribute_value" : "115 cm",
					"abbr" : "115 cm"
				}
			]
		}).save()
	def create_item_template():
	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Cut Cloth",
		"item_name": "Cut Cloth",
		"description": "Cut Cloth",
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
				"attribute" : "Part" 
			},
			{
				"attribute" : "Apparelo Size"
			}
		]
	})
	item.save()
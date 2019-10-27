# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Dyeing(Document):
	def on_submit(self):
		create_item_template()

def create_item_template():
	
	if not frappe.db.exists("Item Attribute", "Apparelo Colour"):
		frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "Apparelo Colour",
			"item_attribute_values": [
				{
					"attribute_value" : "Red",
					"abbr" : "Red"
				},
				{
					"attribute_value" : "Blue",
					"abbr" : "Blue"
				},
				{
					"attribute_value" : "Green",
					"abbr" : "Green"
				},
				{
					"attribute_value" : "Black",
					"abbr" : "Black"
				},
				{
					"attribute_value" : "Navy",
					"abbr" : "Navy"
				},
				{
					"attribute_value" : "A.Mel",
					"abbr" : "A.Mel"
				},
				{
					"attribute_value" : "G.Mel",
					"abbr" : "G.Mel"
				},
				{
					"attribute_value" : "Grey",
					"abbr" : "Grey"
				},
				{
					"attribute_value" : "Brown",
					"abbr" : "Brown"
				},
				{
					"attribute_value" : "Maroon",
					"abbr" : "Maroon"
				}
			]
		}).save()
		

	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "Dyed Cloth",
		"item_name": "Dyed Cloth",
		"description": "Dyed Cloth",
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

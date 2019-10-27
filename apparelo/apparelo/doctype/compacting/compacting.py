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

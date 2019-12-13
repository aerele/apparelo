# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Checking(Document):
	def on_submit(self):
		create_item_template(self)

def create_item_template(self):
	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": self.item+" Checked Cloth",
		"item_name": self.item+" Checked Cloth",
		"description":self.item+" Checked Cloth",
		"item_group": "Sub Assemblies",
		"stock_uom" : "Kg",
		"has_variants" : "1",
		"variant_based_on" : "Item Attribute",
		"attributes" : [
			{
				"attribute" : "Apparelo Colour"
			},
			{
				"attribute" : "Apparelo Size"
			}
		]
	})
	item.save()


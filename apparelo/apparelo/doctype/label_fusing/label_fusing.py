# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LabelFusing(Document):
	def on_submit(self):
		create_item_template(self)

	def create_variants(self, input_item_names):
		pass
def create_item_template(self):
	# todo: need to check if an item already exists with the same name
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": self.item+" Labeled Cloth",
		"item_name": self.item+" Labeled Cloth",
		"description":self.item+" Labeled Cloth",
		"item_group": "Sub Assemblies",
		"stock_uom" : "Nos",
		"has_variants" : "1",
		"variant_based_on" : "Item Attribute",
		"attributes" : [
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
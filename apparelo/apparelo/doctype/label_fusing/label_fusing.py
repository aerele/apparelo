# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LabelFusing(Document):
	def on_submit(self):
		create_item_template()

def create_item_template():
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


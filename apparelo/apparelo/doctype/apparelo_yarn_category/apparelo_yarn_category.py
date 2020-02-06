# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe


class AppareloYarnCategory(Document):
		def validate(self):
			self.create_attribute_value()
		def create_attribute_value(self):
			item_attribute=frappe.get_doc("Item Attribute","Yarn Category")
			yarn_categorys=[]  
			for value in item_attribute.item_attribute_values:
				yarn_categorys.append(value.attribute_value)
			if not self.yarn_category in yarn_categorys:
				item_attribute.append('item_attribute_values',{
					"attribute_value" : self.yarn_category,
					"abbr" : self.yarn_category
				})
				item_attribute.save()

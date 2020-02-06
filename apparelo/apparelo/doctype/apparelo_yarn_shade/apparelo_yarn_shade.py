# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from six import string_types, iteritems
from frappe.model.document import Document

class AppareloYarnShade(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		item_attribute=frappe.get_doc("Item Attribute","Yarn Shade")
		yarn_shade=[]  
		for value in item_attribute.item_attribute_values:
			yarn_shade.append(value.attribute_value)
		if not self.yarn_shade in yarn_shade:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : self.yarn_shade,
				"abbr" : self.yarn_shade
			})
			item_attribute.save()


@frappe.whitelist()
def get_yarn_shade(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	final_yarn_shade=""
	for yarn_shade_ in doc.combined_yarn:
		final_yarn_shade+=yarn_shade_['yarn']+","
	return {"final_yarn_shade":final_yarn_shade[:-1]}

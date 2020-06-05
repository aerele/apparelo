# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from six import string_types, iteritems
from frappe.model.document import Document

class AppareloPart(Document):
	def validate(self):
		self.create_attribute_value()
	def create_attribute_value(self):
		item_attribute=frappe.get_doc("Item Attribute","Part")
		part=[]
		part_name = self.part_name.strip()
		for value in item_attribute.item_attribute_values:
			part.append(value.attribute_value)
		if not part_name in part:
			item_attribute.append('item_attribute_values',{
				"attribute_value" : part_name,
				"abbr" : part_name
			})
			item_attribute.save()
@frappe.whitelist()
def get_combined_parts(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	final_part=""
	for part_ in doc.combined_parts:
		final_part+=part_['parts']+","
	return {"final_part":final_part[:-1]}

# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import hashlib
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def customize_pf_item_code(item_template, attribute_set, variant_attr, variant):
	for dia in attribute_set["Dia"]:
		if dia in variant_attr["Dia"]:
			if not dia+" Dia" in variant:
				hash_=hashlib.sha256(variant.replace(item_template,"").encode()).hexdigest()
				new_variant=item_template+'-'+variant_attr["Dia"][0]+' Dia'+'-'+variant_attr["Apparelo Colour"][0]+'-'+variant_attr["Knitting Type"][0]
				doc=frappe.get_doc("Item",variant)
				doc.print_code=new_variant
				doc.save()
				renamed_variant=frappe.rename_doc("Item",variant,new_variant+" "+hash_[0:7])
				return renamed_variant
			else:
				return variant

def set_custom_fields(update=True):
	custom_fields = {
		'Address': [
			{
				"fieldname": "location",
				"fieldtype": "Link",
				"label": "Location",
				"options": "Location",
				"reqd": 1
				}
			]
		}
	create_custom_fields(custom_fields, ignore_validate=frappe.flags.in_patch, update=update)
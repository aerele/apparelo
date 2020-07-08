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
				new_variant=item_template+'-'+variant_attr["Dia"][0]+' Dia'+'-'+variant_attr["Apparelo Colour"][0].upper()+'-'+variant_attr["Knitting Type"][0].upper()
				doc=frappe.get_doc("Item",variant)
				doc.print_code=new_variant
				doc.save()
				renamed_variant=frappe.rename_doc("Item",variant,new_variant+" "+hash_[0:7])
				return renamed_variant
			else:
				return variant

def set_address_custom_fields(update=True):
	custom_fields = {
		'Address': [
			{
				"fieldname": "location",
				"fieldtype": "Link",
				"label": "Location",
				"options": "Location"
				}
			]
		}
	create_custom_fields(custom_fields, ignore_validate=frappe.flags.in_patch, update=update)

def se_custom_field(update=True):
	custom_fields = {
		'Stock Entry': [
			{
				"fieldname": "dc",
				"fieldtype": "Link",
				"label": "DC",
				"options": "DC"
			}
		]
		}
	create_custom_fields(custom_fields, ignore_validate=frappe.flags.in_patch, update=update)

def create_default_roles():
	roles = ['Apparelo Admin','Data Entry Operator','Report Analyst']
	for role in roles:
		if not frappe.db.exists('Role', role):
			role_doc = frappe.new_doc("Role")
			role_doc.role_name = role
			role_doc.save()
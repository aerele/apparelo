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

def set_user_permissions():
	saved_apparelo_docs = ['Additional Parameters', 'Apparelo Size', 'Apparelo Style', 'Apparelo Dia', 'Apparelo Part', 'Apparelo Colour', 'Apparelo Process', 'Apparelo Settings', 'Apparelo Yarn Shade', 'Knitting Type', 'Multi Process', 'Print Type']
	submittable_apparelo_docs = ['Bleaching', 'Checking', 'Compacting', 'Cutting', 'DC', 'Dyeing', 'GRN', 'Ironing', 'Item Production Detail', 'Knitting','Label Fusing', 'Lot Closure', 'Lot Creation', 'Packing', 'Piece Printing', 'Roll Printing', 'Steaming', 'Stitching']
	data_entry_docs =['DC','GRN','Lot Creation','Lot Closure']
	for apparelo_doc in saved_apparelo_docs:
		doc = frappe.get_doc('DocType',apparelo_doc)
		doc.append('permissions',{'role':'Apparelo Admin','read':1,'write':1,'create':1,'delete':1,'report':1,'export':1,'share':1,'print':1,'email':1})
		doc.save()
	for apparelo_doc in submittable_apparelo_docs:
		doc = frappe.get_doc('DocType',apparelo_doc)
		if apparelo_doc in data_entry_docs:
			doc.append('permissions',{'role':'Apparelo Data Entry Operator','read':1,'write':1,'create':1,'delete':1,'submit':1, 'cancel':1, 'report':1,'export':1,'share':1,'print':1,'email':1})
			doc.append('permissions',{'role':'Apparelo Report Analyst','read':1,'report':1,'export':1,'share':1,'print':1,'email':1})
		doc.append('permissions',{'role':'Apparelo Admin','read':1,'write':1,'create':1,'delete':1,'submit':1, 'cancel':1, 'report':1,'export':1,'share':1,'print':1,'email':1})
		doc.save()

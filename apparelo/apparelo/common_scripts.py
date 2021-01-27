# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import hashlib
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.permissions import add_permission, update_permission_property

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
			},
			{
				"fieldname": "custom_stock_entry",
				"fieldtype": "Link",
				"label": "Custom Stock Entry",
				"options": "Custom Stock Entry",
				"insert_after": "dc"
			}
		]
		}
	create_custom_fields(custom_fields, ignore_validate=frappe.flags.in_patch, update=update)

def create_default_roles():
	roles = ['Apparelo Admin','Apparelo Data Entry Operator','Apparelo Report Analyst']
	for role in roles:
		if not frappe.db.exists('Role', role):
			role_doc = frappe.new_doc("Role")
			role_doc.role_name = role
			role_doc.save()

def set_permissions_to_core_doctypes():
	roles = ['Apparelo Admin', 'Apparelo Data Entry Operator']
	admin_all_permission = ['Item', 'Purchase Order', 'Stock Entry']
	common_read_permission = ['Item Attribute', 'Item Group', 'Warehouse', 'Location', 'Supplier', 'Address', 'Company']
	read_permission_dict = {'Apparelo Admin': ['BOM', 'UOM', 'DocType', 'Material Request', 'Stock Entry Type'], 'Apparelo Data Entry Operator': ['Account', 'Item', 'Purchase Order']}
	
	# assign journal entry create permission to data entry operator.
	add_permission('Journal Entry', 'Apparelo Data Entry Operator', 0)
	update_permission_property('Journal Entry', 'Apparelo Data Entry Operator', 0, 'create', 1)
	
	# assign read permission to the corresponding doctype.
	for role in read_permission_dict.keys():
		for doc in read_permission_dict[role]:
			add_permission(doc, role, 0)
			update_permission_property(doc, role, 0, 'read', 1)
	
	# assign common read permission to both roles.
	for role in roles:
		for doc in common_read_permission:
			add_permission(doc, role, 0)
			update_permission_property(doc, role, 0, 'read', 1)

	# assign all permission to apparelo admin.
	for doc in admin_all_permission:
		add_permission(doc, 'Apparelo Admin', 0)
		if doc != 'Item':
			update_permission_property(doc, 'Apparelo Admin', 0, 'submit', 1)
			update_permission_property(doc, 'Apparelo Admin', 0, 'cancel', 1)
		update_permission_property(doc, 'Apparelo Admin', 0, 'read', 1)
		update_permission_property(doc, 'Apparelo Admin', 0, 'create', 1)
		update_permission_property(doc, 'Apparelo Admin', 0, 'delete', 1)
		update_permission_property(doc, 'Apparelo Admin', 0, 'write', 1)
from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def make_warehouse_custom_fields(update=True):
	custom_fields={'Warehouse': [
	{
	"fieldname": "supplier",
	"fieldtype": "Link",
	"label": "Supplier",
	"options": "Supplier"
		},
	{
	"fieldname": "lot",
	"fieldtype": "Link",
	"label": "Lot",
	"options": "Lot Creation"
		},
	{
	"fieldname": "location",
	"fieldtype": "Link",
	"label": "Location",
	"options": "Location"
		}
	]}
	create_custom_fields(custom_fields,ignore_validate = frappe.flags.in_patch, update=update)
def create_warehouse_type():
	warehouse_type_list=["Actual","Mistake"]
	for warehouse_type in warehouse_type_list:
		if not frappe.db.exists("Warehouse Type",warehouse_type):
			warehouse_type_doc=frappe.new_doc("Warehouse Type")
			warehouse_type_doc.name=warehouse_type
			warehouse_type_doc.save()
from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

default_company = frappe.db.get_single_value(
    'Global Defaults', 'default_company')
abbr = frappe.db.get_value("Company", f"{default_company}", "abbr")


def create_surplus_location_warehouse(doc, action):
    if action == 'validate':
		if not frappe.db.exists("Warehouse", f"Surplus-{doc.name} - {abbr}"):
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"Surplus - {doc.name}",
							"is_group": 0, "parent_warehouse": f"Surplus Warehouse - {abbr}"}).save()
		if not frappe.db.exists("Warehouse", f"Surplus Mistake - {doc.name} - {abbr}"):
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"Surplus Mistake - {doc.name}",
							"is_group": 0, "parent_warehouse": f"Surplus Warehouse - {abbr}"}).save()


def create_supplier_warehouse(doc, action):
    if action == 'validate':
        if not frappe.db.exists("Warehouse", f"{doc.name} - {abbr}"):
            frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"{doc.name}",
                            "is_group": 0, "parent_warehouse": f"Supplier Warehouse - {abbr}"}).save()


def set_lot_link_field_in_po(doc, action):
    if hasattr(doc, 'lot') and action == 'validate':
        for item in doc.items:
            material_request = item.material_request
            break
    material_request_doc = frappe.get_doc("Material Request", material_request)
    doc.lot = material_request_doc.lot
    
    
def set_custom_fields(update=True):
    custom_fields = {
        'Material Request': [
            {
                "fieldname": "lot",
                "fieldtype": "Link",
                "label": "Lot",
                "options": "Lot Creation"
                }
            ],
        'Purchase Receipt': [
            {
                "fieldname": "grn",
                "fieldtype": "Link",
                "label": "GRN",
                "options": "GRN" 
                }
            ]
        }
    create_custom_fields(custom_fields, ignore_validate=frappe.flags.in_patch, update=update)
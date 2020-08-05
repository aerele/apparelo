from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

default_company = frappe.db.get_single_value(
	'Global Defaults', 'default_company')
abbr = frappe.db.get_value("Company", f"{default_company}", "abbr")


def create_location_based_warehouse(doc, action):
	if action == 'after_insert':
		surplus_location_warehouse = frappe.db.get_value("Warehouse", {"parent_warehouse": f"Surplus Warehouse - {abbr}", "location": doc.name, "warehouse_type": "Actual"}, "name")
		surplus_mistake_warehouse = frappe.db.get_value("Warehouse", {"parent_warehouse": f"Surplus Mistake Warehouse - {abbr}", "location": doc.name, "warehouse_type": "Mistake"}, "name")
		stores_location_warehouse = frappe.db.get_value("Warehouse", {"parent_warehouse": f"Stores - {abbr}", "location": doc.name}, "name")
		if not surplus_location_warehouse:
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"Surplus - {doc.name}","location": doc.name,"warehouse_type":"Actual",
						"is_group": 0, "parent_warehouse": f"Surplus Warehouse - {abbr}"}).save()
		if not surplus_mistake_warehouse:
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"Surplus Mistake - {doc.name}","location": doc.name,"warehouse_type": "Mistake",
							"is_group": 0, "parent_warehouse": f"Surplus Mistake Warehouse - {abbr}"}).save()
		if not stores_location_warehouse:
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"Stores - {doc.name}", "location": doc.name, "warehouse_type": "Actual",
							"is_group": 0, "parent_warehouse": f"Stores - {abbr}"}).save()


def create_supplier_warehouse(doc, action):
	if action == 'after_insert':
		supplier_warehouse= frappe.db.get_value("Warehouse",{'supplier':doc.name},"name")
		if not supplier_warehouse:
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"{doc.name}","supplier": doc.name,
							"is_group": 0, "parent_warehouse": f"Supplier Warehouse - {abbr}",
							"company": default_company}).save()


def set_lot_link_field_in_po(doc, action):
	if hasattr(doc, 'lot') and action == 'validate':
		material_request = doc.items[0].material_request
		if material_request:
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

def change_stores_warehouse():
	warehouse_name = f'Stores - {abbr}'
	if frappe.db.exists('Warehouse',warehouse_name):
		warehouse = frappe.get_doc('Warehouse',warehouse_name)
		warehouse.is_group = 1
		warehouse.save()
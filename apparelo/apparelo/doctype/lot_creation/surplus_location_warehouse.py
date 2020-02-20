from __future__ import unicode_literals
import frappe

default_company = frappe.db.get_single_value(
	'Global Defaults', 'default_company')
abbr = frappe.db.get_value("Company", f"{default_company}", "abbr")


def create_surplus_location_warehouse(doc, method):
	if not frappe.db.exists("Warehouse", f"Surplus-{doc.name} - {abbr}"):
		frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"Surplus - {doc.name}",
						"is_group": 0, "parent_warehouse": f"Surplus Warehouse - {abbr}"}).save()
	if not frappe.db.exists("Warehouse", f"Surplus Mistake - {doc.name} - {abbr}"):
		frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"Surplus Mistake - {doc.name}",
						"is_group": 0, "parent_warehouse": f"Surplus Warehouse - {abbr}"}).save()


def create_supplier_warehouse(doc, method):
	if not frappe.db.exists("Warehouse", f"{doc.name} - {abbr}"):
		frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"{doc.name}",
						"is_group": 0, "parent_warehouse": f"Supplier Warehouse - {abbr}"}).save()

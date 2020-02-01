from __future__ import print_function, unicode_literals

import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from apparelo.apparelo.doctype.knitting import knitting
from apparelo.apparelo.doctype.dyeing import dyeing
from apparelo.apparelo.doctype.bleaching import bleaching
from apparelo.apparelo.doctype.compacting import compacting
from apparelo.apparelo.doctype.steaming import steaming
from apparelo.apparelo.doctype.cutting import cutting
from apparelo.apparelo.doctype.roll_printing import roll_printing
from apparelo.apparelo.doctype.dc.dc import make_custom_fields
from apparelo.apparelo.doctype.dc.dc import make_item_fields
from apparelo.apparelo.doctype.additional_parameters import additional_parameters
from apparelo.apparelo.doctype.apparelo_dia import apparelo_dia

def after_install():
    remove_defaults()
    create_new_uom()
    create_item_attributes()
    create_attr_values()
    create_item_template()
    make_item_fields()
    make_custom_fields()
    create_root_warehouse()

def create_item_attributes():
    knitting.create_item_attribute()
    dyeing.create_item_attribute()
    cutting.create_item_attribute()
    roll_printing.create_item_attribute()

def create_item_template():
    knitting.create_item_template()
    dyeing.create_item_template()
    bleaching.create_item_template()
    compacting.create_item_template()
    steaming.create_item_template()
    roll_printing.create_item_template()

def create_attr_values():
    knitting.create_attr_values()
    knitting.create_additional_attribute()
    additional_parameters.create_parameter()
    apparelo_dia.populate()

def remove_defaults():
    stock_setting=frappe.get_doc("Stock Settings")
    stock_setting.stock_uom=None
    stock_setting.save()

def create_new_uom():
    if not frappe.get_doc("UOM","Combined Part"):
        uom=frappe.new_doc("UOM")
        uom.uom_name= 'Combined Part'
        uom.save()

def create_root_warehouse():
    default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
    abbr = frappe.db.get_value("Company", f"{default_company}", "abbr")
    warehouses = ["Lot Warehouse","Supplier Warehouse"]
    for name in warehouses:
        if not frappe.db.exists("Warehouse", f'{name} - {abbr}'):
            frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": name,
                "is_group": 1,
                "parent_warehouse": f"All Warehouses - {abbr}"
            }).save()

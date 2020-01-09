from __future__ import unicode_literals
import frappe

def execute():
    frappe.reload_doc('Apparelo', 'doctype', 'Apparelo Size')
    frappe.reload_doc('Apparelo', 'doctype', 'Apparelo Colour')
    frappe.reload_doc('Apparelo', 'doctype', 'Apparelo Part')
    frappe.reload_doc('Apparelo', 'doctype', 'Knitting Type')
    from apparelo.apparelo.doctype.knitting.knitting import create_attr_values
    create_attr_values()
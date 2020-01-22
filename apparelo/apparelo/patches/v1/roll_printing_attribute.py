from __future__ import unicode_literals
import frappe

def execute():
    frappe.reload_doc('Apparelo', 'doctype', 'Print Type')
    from apparelo.apparelo.doctype.knitting.knitting import create_additional_attribute
    create_additional_attribute()
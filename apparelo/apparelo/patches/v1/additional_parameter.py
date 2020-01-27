from __future__ import unicode_literals
import frappe

def execute():
    frappe.reload_doc('Apparelo', 'doctype', 'Additional Parameters')
    from apparelo.apparelo.doctype.additional_parameters import additional_parameters
    additional_parameters.create_parameter()
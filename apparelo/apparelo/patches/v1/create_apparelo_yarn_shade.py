from __future__ import unicode_literals
import frappe

def execute():
    frappe.reload_doc('Apparelo', 'doctype', 'Apparelo Yarn Shade', force=True)
    from apparelo.apparelo.doctype.apparelo_yarn_shade.apparelo_yarn_shade import populate
    populate()
from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.install import create_roll_uom
    from apparelo.apparelo.doctype.apparelo_process.apparelo_process import create_apparelo_process
    frappe.reload_doc('Apparelo', 'doctype', 'Apparelo Process')
    create_roll_uom()
    create_apparelo_process()
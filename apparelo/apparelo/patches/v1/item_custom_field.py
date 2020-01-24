from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.apparelo.doctype.dc.dc import make_item_fields
    make_item_fields()

from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.apparelo.doctype.knitting import knitting
    knitting.create_striped_item_template()
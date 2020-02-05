from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.install import create_new_uom
    create_new_uom()
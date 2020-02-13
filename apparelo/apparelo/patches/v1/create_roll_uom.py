from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.install import create_roll_uom
    create_roll_uom()
from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.install import create_bags_uom
    create_bags_uom()
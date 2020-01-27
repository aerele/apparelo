from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.install import create_lot_warehouse
    create_lot_warehouse()
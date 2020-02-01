from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.install import create_root_warehouse
    create_root_warehouse()
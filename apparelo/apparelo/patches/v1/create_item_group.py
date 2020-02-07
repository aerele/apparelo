
from __future__ import unicode_literals
import frappe

def execute():
    from apparelo.install import create_item_group
    create_item_group()
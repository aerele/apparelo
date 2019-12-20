from __future__ import print_function, unicode_literals

import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from apparelo.apparelo.doctype import knitting,dyeing,bleaching,compacting,steaming,cutting,piece_printing,stitching,label_fusing,checking,ironing,packing

def after_install():
    knitting.Knitting.on_submit()
    dyeing.Dyeing.on_submit()
    bleaching.Bleaching.on_submit()
    compacting.Compacting.on_submit()
    steaming.Steaming.on_submit()
    cutting.Cutting.on_submit()
    piece_printing.PiecePrinting.on_submit()
    stitching.Stitching.on_submit()
    label_fusing.LabelFusing.on_submit()
    checking.Checking.on_submit()
    ironing.Ironing.on_submit()
    packing.Packing.on_submit()

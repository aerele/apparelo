# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import hashlib

def customize_pf_item_code(item_template, attribute_set, variant_attr, variant):
    for dia in attribute_set["Dia"]:
        if dia in variant_attr["Dia"]:
            if not dia+" Dia" in variant:
                hash_=hashlib.sha256(variant.replace(item_template,"").encode()).hexdigest()
                new_variant=variant.replace(dia,dia+" Dia").replace('-'+variant_attr['Yarn Shade'][0].upper(),'').replace('-'+variant_attr['Yarn Count'][0],'').replace('-'+variant_attr['Yarn Category'][0].upper(),'')
                doc=frappe.get_doc("Item",variant)
                doc.print_code=new_variant
                doc.save()
                renamed_variant=frappe.rename_doc("Item",variant,new_variant+" "+hash_[0:7])
                return renamed_variant
            else:
                return variant
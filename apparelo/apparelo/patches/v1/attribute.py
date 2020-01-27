from __future__ import unicode_literals
import frappe

def execute():
    attribute_value=['Folding','Net Folding']
    create_attribute_value(attribute_value)


def create_attribute_value(attribute_value):
    item_attribute=frappe.get_doc("Item Attribute","Part")
    part=[]  
    for value in item_attribute.item_attribute_values:
        part.append(value.attribute_value)
    for attribute_ in attribute_value:
        if not attribute_ in part:
            item_attribute.append('item_attribute_values',{
                "attribute_value" : attribute_,
                "abbr" : attribute_
            })
            item_attribute.save()

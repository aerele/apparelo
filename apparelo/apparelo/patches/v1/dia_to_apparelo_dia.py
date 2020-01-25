import frappe
from __future__ import unicode_literals

def execute():
  modify_dia_item_attribute()
  
def modify_dia_item_attribute():
	dia_item_attribute = frappe.get_doc("Item Attribute", "Dia")
	dia_item_attribute.numeric_values = 0
	dia_item_attribute.from_range = None
	dia_item_attribute.to_range = None
	dia_item_attribute.increment = None
	for i in range(40, 165, 1):
		i = i * 0.25
		if int(str(i).split('.')[1]) == 0:
			i = str(i).split('.')[0]
		elif int(str(i).split('.')[1]) == 5:
				i = str(i) + '0'
		apparelo_dia = frappe.new_doc("Apparelo Dia")
		apparelo_dia.dia = str(i)
		apparelo_dia.save()
		dia_item_attribute.append('item_attribute_values',{
			"attribute_value" : str(i),
			"abbr" : str(i)
		})
	dia_item_attribute.save()
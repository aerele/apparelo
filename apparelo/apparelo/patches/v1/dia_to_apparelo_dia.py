from __future__ import unicode_literals
import frappe

def execute():
	modify_dia_item_attribute()

def modify_dia_item_attribute():
	frappe.reload_doc('Apparelo', 'doctype', 'Apparelo Dia', force=True)
	dia_item_attribute = frappe.get_doc("Item Attribute", "Dia")
	dia_item_attribute.numeric_values = 0
	dia_item_attribute.from_range = None
	dia_item_attribute.to_range = None
	dia_item_attribute.increment = None
	for i in range(40, 165, 1):
		i = i * 0.25
		if int(str(i).split('.')[1]) == 0:
			i = str(i).split('.')[0]
		dia_item_attribute.append('item_attribute_values',{
			"attribute_value" : str(i),
			"abbr" : str(i)
		})
	dia_item_attribute.save()

	for i in range(40, 165, 1):
		i = i * 0.25
		if int(str(i).split('.')[1]) == 0:
			i = str(i).split('.')[0]
		apparelo_dia = frappe.new_doc("Apparelo Dia")
		apparelo_dia.dia = str(i)
		apparelo_dia.save()

	frappe.reload_doc('Apparelo', 'doctype', 'Knitting Dia', force=True)
	frappe.reload_doc('Apparelo', 'doctype', 'Steaming Dia Conversion', force=True)
	frappe.reload_doc('Apparelo', 'doctype', 'Cutting Detail', force=True)

	frappe.db.sql("""update `tabCutting Detail` set dia = trim(trailing '0' from dia);""")
	frappe.db.sql("""update `tabCutting Detail` set dia = trim(trailing '.' from dia);""")

	frappe.db.sql("""update `tabKnitting Dia` set dia = trim(trailing '0' from dia);""")
	frappe.db.sql("""update `tabKnitting Dia` set dia = trim(trailing '.' from dia);""")

	frappe.db.sql("""update `tabSteaming Dia Conversion` set from_dia = trim(trailing '0' from from_dia);""")
	frappe.db.sql("""update `tabSteaming Dia Conversion` set from_dia = trim(trailing '.' from from_dia);""")

	frappe.db.sql("""update `tabSteaming Dia Conversion` set to_dia = trim(trailing '0' from to_dia);""")
	frappe.db.sql("""update `tabSteaming Dia Conversion` set to_dia = trim(trailing '.' from to_dia);""")

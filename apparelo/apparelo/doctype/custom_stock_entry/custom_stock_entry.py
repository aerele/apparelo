# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from six import string_types
from apparelo.apparelo.utils.item_utils import get_item_attribute_set
from erpnext import get_default_company
from frappe import _, msgprint
from frappe.utils import comma_and

class CustomStockEntry(Document):
	def on_cancel(self):
		self.db_set("docstatus",2)
		msgprint(_("{0} cancelled").format(comma_and("""<a href="#Form/Custom Stock Entry/{0}">{1}</a>""".format(self.name, self.name))))
	
	def on_submit(self):
		items = []
		for item in self.stock_entry_items:
			item_list = {}
			item_list['item_code'] = item.item_code
			item_list['item_name'] = item.item_code
			item_list['qty'] = item.qty
			item_list['basic_rate'] = 1.00
			item_list['t_warehouse'] = self.default_target_warehouse
			item_list['stock_uom'] = item.uom
			items.append(item_list)
		stock_entry = frappe.get_doc({
				"doctype": "Stock Entry",
				"custom_stock_entry": self.name,
				"to_warehouse": self.default_target_warehouse,
				"stock_entry_type": 'Material Receipt',
				"company": get_default_company(),
				"items":items})
		stock_entry.save()
		stock_entry.submit()
		msgprint(_("{0} created").format(comma_and(
			"""<a href="#Form/Stock Entry/{0}">{1}</a>""".format(stock_entry.name, stock_entry.name))))

@frappe.whitelist()
def get_inward_item(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))

	lot = doc.get('lot')
	process = doc.get('process_1')
	apparelo_process = frappe.get_doc("Apparelo Process", process)
	lot_ipd = frappe.db.get_value(
		'Lot Creation', {'name': lot}, 'item_production_detail')

	ipd_bom_mapping = frappe.db.get_value(
		'IPD BOM Mapping', {'item_production_details': lot_ipd})
	ipd_item_mapping = frappe.get_doc(
		"IPD Item Mapping", {'item_production_details': lot_ipd})
	boms = frappe.get_doc(
		'IPD BOM Mapping', ipd_bom_mapping).get_process_boms(process)
	inward_item = frappe.get_list('BOM', filters={'name': ['in', boms]},
					group_by='item', fields=['item', 'name as bom'])

	item_mapping_validator = [x["item"] for x in frappe.get_list(
		"Item Mapping", {"parent": ipd_item_mapping.name, "process_1": process}, "item")]
	inward_item_with_removed_invalids_list = []
	for item in inward_item:
		if item['item'] in item_mapping_validator:
			inward_item_with_removed_invalids_list.append(
				item)

	inward_item = inward_item_with_removed_invalids_list

	lot_ipd_doc = frappe.get_doc("Item Production Detail", lot_ipd)
	for item in inward_item:
		item_doc = frappe.get_doc('Item', item['item'])
		item['item_code'] = item['item']
		item['uom'] = item_doc.stock_uom
		for attr in item_doc.attributes:
			if attr.attribute == "Apparelo Size":
				item['Apparelo Size'] = attr.attribute_value
			if attr.attribute == "Dia":
				item['Dia'] = attr.attribute_value
			if attr.attribute == "Apparelo Colour":
				item['Apparelo Colour'] = attr.attribute_value

	if 'Dia' in item:
		if 'Apparelo Colour' in item:
			inward_item = sorted(sorted(inward_item, key = lambda i: i['Dia']), key = lambda i: i['Apparelo Colour'])
		else:
			inward_item = sorted(inward_item, key = lambda i: i['Dia'])
	if 'Apparelo Size' in item:
		inward_item = sorted(inward_item, key = lambda i: i['Apparelo Size'])

	return inward_item

@frappe.whitelist()
def make_entry(doc):
	return_items_after_entry = []
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	inward_item = get_inward_item(doc)
	size = doc.size
	colour = doc.colour
	piece_count = doc.piece_count 
	ipd = frappe.db.get_value('Lot Creation',{'name': doc.get('lot')},'item_production_detail')
	process_record_list = frappe.get_list("Item Production Detail Process",{'parent': ipd,'process_name':'Stitching'},'process_record')
	if len(process_record_list)>1:
		frappe.throw(_(f'Unable to proceed with more than one stitching process record'))
	else:
		colour_mappings = frappe.get_list("Stitching",filters={'name':['in',[process_record_list[0]['process_record']]]},fields=["`tabStitching Colour Mapping`.part","`tabStitching Colour Mapping`.piece_colour","`tabStitching Colour Mapping`.part_colour"])
		parts_per_pieces = frappe.get_list("Stitching",filters={'name':['in',[process_record_list[0]['process_record']]]},fields=["`tabStitching Parts Per Piece`.part","`tabStitching Parts Per Piece`.qty"])
		for item in inward_item:
			item_dict={}
			count=0
			item_doc = frappe.get_doc('Item', item['item_code'])
			attribute_set = get_item_attribute_set(list(map(lambda x: x.attributes, [item_doc])))
			for colour_mapping in colour_mappings:
				for parts_per_piece in parts_per_pieces:
					if attribute_set["Part"][0] == parts_per_piece.part and attribute_set["Part"][0] == colour_mapping.part and attribute_set['Apparelo Size'][0] == size:
						if colour_mapping.piece_colour == colour and colour_mapping.part_colour == attribute_set["Apparelo Colour"][0]:
								count+=1
								piece_qty = parts_per_piece.qty
			if count==1:
				item_dict = {"item_code":item['item_code'],"qty":piece_count*piece_qty,"uom":item['uom']}
				return_items_after_entry.append(item_dict)
	return return_items_after_entry

@frappe.whitelist()
def delete_unavailable_items(doc):
	available_items = []
	if isinstance(doc, string_types):
    		doc = frappe._dict(json.loads(doc))
	for item in doc.get('stock_entry_items'):
		item_dict={}
		if item['qty']!=0:
			item_dict = {"item_code":item['item_code'],"qty":item['qty'],"uom":item['uom']}
		if item_dict:
			available_items.append(item_dict)
	return available_items
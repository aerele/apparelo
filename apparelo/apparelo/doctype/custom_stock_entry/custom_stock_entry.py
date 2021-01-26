# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from six import string_types

class CustomStockEntry(Document):
	def on_submit(self):
		items = []
		for item in self.stock_entry_items:
			item_list = {}
			item_list['item_code'] = item.item_code
			item_list['item_name'] = item.item_code
			item_list['qty'] = item.qty
			item_list['t_warehouse'] = self.default_target_warehouse
			item_list['stock_uom'] = item.uom
			item_list['allow_zero_valuation_rate'] = 1
			items.append(item_list)
		stock_entry = frappe.get_doc({
				"doctype": "Stock Entry",
				"to_warehouse": self.default_target_warehouse,
				"stock_entry_type": 'Material Receipt',
				"items":items})
		stock_entry.save()
		stock_entry.submit()

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
	items_to_be_received = frappe.get_list('BOM', filters={
										   'name': ['in', boms]}, group_by='item', fields=['item', 'name as bom'])

	item_mapping_validator = [x["item"] for x in frappe.get_list(
		"Item Mapping", {"parent": ipd_item_mapping.name, "process_1": process}, "item")]
	items_to_be_received_with_removed_invalids_list = []
	for item_to_be_received in items_to_be_received:
		if item_to_be_received['item'] in item_mapping_validator:
			items_to_be_received_with_removed_invalids_list.append(
				item_to_be_received)

	items_to_be_received = items_to_be_received_with_removed_invalids_list

	lot_ipd_doc = frappe.get_doc("Item Production Detail", lot_ipd)
	for item_to_be_received in items_to_be_received:
		item = frappe.get_doc('Item', item_to_be_received['item'])
		item_to_be_received['item_code'] = item_to_be_received['item']
		item_to_be_received['uom'] = item.stock_uom

	return items_to_be_received
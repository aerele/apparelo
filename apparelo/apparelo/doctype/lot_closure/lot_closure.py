# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
from six import string_types
from frappe.model.document import Document
import collections
from erpnext.stock.report.stock_balance.stock_balance import execute
from datetime import datetime
from frappe.utils import getdate, now_datetime, nowdate


class LotClosure(Document):
	def on_submit(self):
		if self.enable_repack_items:
			self.repack_stock_entry()
		self.make_stock_entry()
		lot_doc = frappe.get_doc("Lot Creation", self.lot)
		lot_doc.lot_status = 'Closed'
		lot_doc.save()
	def make_stock_entry(self):
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.stock_entry_type = 'Send to Warehouse'
		for item in self.lot_closure_items:
			item_list = {}
			if item.new_item_code:
				if is_valid_item(item.item_code, item.new_item_code):
					item_list['item_code'] = item.new_item_code
				else:
					frappe.throw(_("Invalid new item code selected in the row {0}".format(self.lot_closure_items.index(item))))
			else:
				item_list['item_code'] = item.item_code
			item_list['s_warehouse'] = item.warehouse
			item_list['t_warehouse'] = item.target_warehouse
			item_list['qty'] = item.bal_qty
			item_list['uom'] = item.stock_uom
			stock_entry.append('items', item_list)
		stock_entry.save()
		stock_entry.submit()
	def repack_stock_entry(self):
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.stock_entry_type = 'Repack'
		for item in self.lot_closure_items:
			if item.new_item_code:
				if is_valid_item(item.item_code, item.new_item_code):
					repack_item_list = {}
					repack_item_list['item_code'] = item.item_code
					repack_item_list['s_warehouse'] = item.warehouse
					repack_item_list['qty'] = item.bal_qty
					repack_item_list['uom'] = item.stock_uom
					stock_entry.append('items', repack_item_list)
					repack_item_list = {}
					repack_item_list['item_code'] = item.new_item_code
					repack_item_list['t_warehouse'] = item.warehouse
					repack_item_list['qty'] = item.bal_qty
					repack_item_list['uom'] = item.stock_uom
					stock_entry.append('items', repack_item_list)
				else:
					frappe.throw(_("Invalid new item code selected in the row {0}".format(self.lot_closure_items.index(item)+1)))
		stock_entry.save()
		stock_entry.submit()
@frappe.whitelist()
def get_lot_closure_details(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	lot = doc.get('lot')
	po_items = frappe.get_list(
		"Purchase Order",
		filters={'lot':lot, 'is_subcontracted':'yes'},
		fields=[
			'name',
			'supplier',
			"`tabPurchase Order Item Supplied`.rm_item_code",
			"`tabPurchase Order Item Supplied`.supplied_qty"
			])
	po_names = list(set([po["name"] for po in po_items]))
	pr_list = frappe.get_list(
		"Purchase Receipt Item",
		filters={'purchase_order': ['in', po_names]},
		fields=['parent'], group_by='parent'
		)
	pr_names = [pr["parent"] for pr in pr_list]
	pr_items = frappe.get_list(
		"Purchase Receipt",
		filters={'name': ['in', pr_names], 'is_subcontracted': 'yes'},
		fields=[
			'name',
			'supplier',
			"`tabPurchase Receipt Item Supplied`.rm_item_code",
			"`tabPurchase Receipt Item Supplied`.consumed_qty"
			])
	lot_closure_details = get_combined_final_list(po_items, pr_items)
	lot_closure_details = sorted(lot_closure_details, key = lambda item: abs(item['difference']), reverse=True)
	return lot_closure_details


def get_combined_final_list(po_items, pr_items):
	all_items = sorted(po_items+pr_items, key=lambda x: (x['supplier'], x['rm_item_code']))
	final_item_list = []
	import itertools
	for key, group in itertools.groupby(all_items, key=lambda x: (x['supplier'], x['rm_item_code'])):
		total_supplied_qty = 0
		total_consumed_qty = 0
		po_list = []
		pr_list = []
		for item in group:
			print(item)
			if 'supplied_qty' in item:
				print('in sup')
				total_supplied_qty += item['supplied_qty']
				if item['name'] not in po_list:
					po_list.append(item['name'])
				print(po_list)
			elif 'consumed_qty' in item:
				print('in cons')
				total_consumed_qty += item['consumed_qty']
				if item['name'] not in pr_list:
					pr_list.append(item['name'])
				print(pr_list)
		final_item = {
			'supplier': key[0],
			'rm_item_code': key[1],
			'supplied_qty': total_supplied_qty,
			'consumed_qty': total_consumed_qty,
			'po': ','.join(po_list),
			'pr': ','.join(pr_list),
			'difference': -((total_supplied_qty - total_consumed_qty)/total_supplied_qty)*100 if total_supplied_qty else 0
		}
		final_item_list.append(final_item)
	return final_item_list


@frappe.whitelist()
def get_lot_closure_items(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	lot_closure_items = []
	item_group = doc.get('item_group')
	lot = doc.get('lot')
	target_warehouse = doc.get('warehouse')
	lot_start_date = frappe.db.get_value("Lot Creation",{'name':'GY-1'},'start_date').strftime("%d-%m-%Y")
	now_date = getdate(nowdate()).strftime("%d-%m-%Y")
	lot_warehouse = frappe.db.get_value("Warehouse",{'warehouse_name': lot},"name")
	col, stock_balance_datas = execute(filters=frappe._dict({'item_group': item_group, 'warehouse':lot_warehouse, 'from_date':frappe.utils.get_datetime(lot_start_date), 'to_date':frappe.utils.get_datetime(now_date)}))
	if doc.get('lot_closure_items') != None:
		for item in doc.get('lot_closure_items'):
			lot_closure_items.append({'item_code':item['item_code'], 'bal_qty':item['bal_qty'], 'warehouse':item['warehouse'], 'target_warehouse':item['target_warehouse'], 'stock_uom':item['stock_uom']})
	for data in stock_balance_datas:
		data['target_warehouse'] = target_warehouse
	lot_closure_items.extend(stock_balance_datas)
	return lot_closure_items

def is_valid_item(old_item,new_item):
	old_item_attribute_list = frappe.get_list("Item", filters={'name': ['in',old_item]}, fields=["`tabItem Variant Attribute`.attribute","`tabItem Variant Attribute`.attribute_value"])
	new_item_attribute_list = frappe.get_list("Item", filters={'name': ['in',new_item]}, fields=["`tabItem Variant Attribute`.attribute","`tabItem Variant Attribute`.attribute_value"])
	if old_item_attribute_list == new_item_attribute_list:
		return True
	else:
		return False
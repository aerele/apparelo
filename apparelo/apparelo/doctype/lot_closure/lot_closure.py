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
		self.make_stock_entry()
		lot_doc=frappe.get_doc("Lot Creation",self.lot)
		lot_doc.lot_status='Closed'
		lot_doc.save()
	def make_stock_entry(self):
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.stock_entry_type='Send to Warehouse'
		rm_items = []
		for item in self.lot_closure_items:
				item_list = {}
				if item.new_item_code:
					if is_valid_item(item.item_code,item.new_item_code):
						item_list['item_code'] = item.new_item_code
					else:
						frappe.throw(_("Invalid new item code selected in the row {0}".format(self.lot_closure_items.index(item))))
				else:
					item_list['item_code'] = item.item_code
				item_list['s_warehouse'] = item.warehouse
				item_list['t_warehouse'] = item.target_warehouse
				item_list['qty'] = item.bal_qty
				item_list['uom']=item.stock_uom
				rm_items.append(item_list)
				stock_entry.append('items',item_list)
		stock_entry.save()
		stock_entry.submit()
		
@frappe.whitelist()
def get_lot_closure_details(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	doc['lot_closure_details'] = []
	lot_closure_details=[]
	lot=doc.get('lot')
	pr_list=[]
	po_list=frappe.get_list("Purchase Order", filters={'lot':lot})
	po_names=[po["name"] for po in po_list]
	po_items=frappe.get_list("Purchase Order", filters={'name': ['in',po_names],'is_subcontracted':['in','yes']}, fields=['supplier',"`tabPurchase Order Item Supplied`.rm_item_code","`tabPurchase Order Item Supplied`.supplied_qty"])
	for po in po_names:
		pr_list.extend(frappe.get_list("Purchase Receipt Item", filters={'purchase_order': ['in',po]}, fields=['parent'],group_by='parent'))
	pr_names=[pr["parent"] for pr in pr_list]
	pr_items=frappe.get_list("Purchase Receipt", filters={'name': ['in',pr_names], 'is_subcontracted':['in','yes']}, fields=['supplier',"`tabPurchase Receipt Item Supplied`.rm_item_code","`tabPurchase Receipt Item Supplied`.consumed_qty"])
	po_items=get_combined_item_list(po_items,'supplied_qty')
	pr_items=get_combined_item_list(pr_items,'consumed_qty')
	po_items.extend(pr_items)
	lot_closure_details=get_final_list(po_items)
	lot_closure_details=sorted(lot_closure_details, key = lambda item: item['difference'])
	return lot_closure_details

def get_combined_item_list(item_list,qty_field):
	combined_list= [list(item.values()) for item in item_list]
	combined_list=[[items[0],items[1],items[2]] for items in combined_list]
	collection_list = collections.defaultdict(list)
	for fields in combined_list:
		collection_list[fields[0],fields[1]].append(fields[2])
	final_items=list(collection_list.items())
	final_list=[]
	for field in final_items:
		new_list=list(field[0])
		new_list.append(sum(field[1]))
		final_list.append(new_list)
	final_item_list=[{'rm_item_code':final_item[1],qty_field:final_item[2],'supplier':final_item[0]}for final_item in final_list]
	return final_item_list

def get_final_list(item_list):
	for index in range(len(item_list)):                                                              
		for next_index in range(index+1,len(item_list)):
			if index!=next_index and item_list[index]['rm_item_code']==item_list[next_index]['rm_item_code'] and item_list[index]['supplier']==item_list[next_index]['supplier']:
				item_list[next_index]['difference']=''
				item_list[next_index]['difference']=str((round(item_list[next_index]['consumed_qty']-item_list[index]['supplied_qty']))*100)
				po_list=frappe.get_list("Purchase Order",filters={'supplier': ['in',item_list[next_index]['supplier']]})
				po_names=''
				pr_names=''
				for po in po_list:
					po_names=",".join(po["name"])
				pr_list=frappe.get_list("Purchase Receipt",filters={'supplier': ['in',item_list[next_index]['supplier']]})
				for pr in pr_list:
					pr_names=",".join(pr["name"])
				item_list[next_index]['po']=po_names
				item_list[next_index]['pr']=pr_names
				item_list[index].update(item_list[next_index])
				item_list.remove(item_list[next_index])
				break
	return item_list

@frappe.whitelist()
def get_lot_closure_items(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	lot_closure_items=[]
	item_group=doc.get('item_group')
	lot=doc.get('lot')
	target_warehouse=doc.get('warehouse')
	lot_start_date=frappe.db.get_value("Lot Creation",{'name':'GY-1'},'start_date').strftime("%d-%m-%Y")
	now_date = getdate(nowdate()).strftime("%d-%m-%Y")
	lot_warehouse= frappe.db.get_value("Warehouse",{'warehouse_name': lot},"name")
	col, datas = execute(filters=frappe._dict({'item_group': item_group,'warehouse':lot_warehouse,'from_date':frappe.utils.get_datetime(lot_start_date),'to_date':frappe.utils.get_datetime(now_date)}))
	if doc.get('lot_closure_items') != None:
		for item in doc.get('lot_closure_items'):
			lot_closure_items.append({'item_code':item['item_code'],'bal_qty':item['bal_qty'],'warehouse':item['warehouse'],'target_warehouse':item['target_warehouse'],'stock_uom':item['stock_uom']})
	for data in datas:
		data['target_warehouse']=target_warehouse
	lot_closure_items.extend(datas)
	return lot_closure_items

def is_valid_item(old_item,new_item):
	old_item_attribute_list=frappe.get_list("Item", filters={'name': ['in',old_item]}, fields=["`tabItem Variant Attribute`.attribute","`tabItem Variant Attribute`.attribute_value"])
	new_item_attribute_list=frappe.get_list("Item", filters={'name': ['in',new_item]}, fields=["`tabItem Variant Attribute`.attribute","`tabItem Variant Attribute`.attribute_value"])
	if old_item_attribute_list==new_item_attribute_list:
		return True
	else:
		return False
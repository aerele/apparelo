# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from six import string_types
from frappe.model.document import Document
import collections 

class LotClosure(Document):
	pass
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
				po_names=[po["name"] for po in po_list]
				pr_list=frappe.get_list("Purchase Receipt",filters={'supplier': ['in',item_list[next_index]['supplier']]})
				pr_names=[pr["name"] for pr in pr_list]
				item_list[next_index]['po']=po_names
				item_list[next_index]['pr']=pr_names
				item_list[index].update(item_list[next_index])
				item_list.remove(item_list[next_index])
				break
	return item_list

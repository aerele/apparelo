# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _, msgprint
from six import string_types, iteritems
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil
from erpnext.stock.report.stock_balance.stock_balance import execute
from erpnext.buying.doctype.purchase_order.purchase_order import make_rm_stock_entry
from erpnext import get_default_company
from erpnext.manufacturing.doctype.production_plan.production_plan import get_items_for_material_requests


class DC(Document):
			
    def on_submit(self):
        new_po = self.create_purchase_order()
        rm_items = []
        for item in new_po.supplied_items:
            item_list = {}
            item_list['name'] = item.name
            item_list['item_code'] = item.main_item_code
            item_list['rm_item_code'] = item.rm_item_code
            item_list['item_name'] = item.rm_item_code
            item_list['qty'] = item.required_qty
            item_list['warehouse'] = item.reserve_warehouse
            item_list['rate'] = item.rate
            item_list['amount'] = item.amount
            item_list['stock_uom'] = item.stock_uom
            rm_items.append(item_list)
        stock_dict = make_rm_stock_entry(new_po.name, json.dumps(rm_items))
        stock_entry = frappe.get_doc(stock_dict)
        stock_entry.save()
        stock_entry.submit()

        msgprint(_("{0} created").format(comma_and(
            """<a href="#Form/Purchase Order/{0}">{1}</a>""".format(new_po.name, new_po.name))))
        msgprint(_("{0} created").format(comma_and(
            """<a href="#Form/Stock Entry/{0}">{1}</a>""".format(stock_entry.name, stock_entry.name))))

    def create_purchase_order(self):
        dc_items = []
        supplied_items = []
        lot_warehouse = frappe.db.get_value("Warehouse", {
                                            'location': self.location, 'lot': self.lot, 'warehouse_type': "Actual"}, 'name')
        supplier_warehouse = frappe.db.get_value(
            "Warehouse", {'supplier': self.supplier}, 'name')
        for item_ in self.return_materials:
            dc_items.append(
                {"item_code": item_.item_code,
                 "schedule_date": add_days(nowdate(), 7),
                 "qty": item_.qty,
                 "bom": item_.bom,
                 "rate": 1
                 })
        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": self.supplier,
            "dc": self.name,
            "lot": self.lot,
            "schedule_date": add_days(nowdate(), 7),
            "set_warehouse": lot_warehouse,
            "set_reserve_warehouse": lot_warehouse,
            "is_subcontracted": "Yes",
            "supplier_warehouse": supplier_warehouse,
            "items": dc_items})
        po.save()
        # set_reserve_warehouse related code does not exist in python hence the following is required
        for item in po.supplied_items:
            item.reserve_warehouse = lot_warehouse
        po.save()
        po.submit()
        return po


def get_supplier(doctype, txt, searchfield, start, page_len, filters):
    suppliers = []
    all_supplier = frappe.db.get_all("Supplier")
    for supplier in all_supplier:
        process_supplier = frappe.get_doc("Supplier", supplier.name)
        for process in process_supplier.supplier_process:
            if process.processes == filters['supplier_process.processes']:
                suppliers.append([supplier.name])
    return suppliers


def make_item_fields(update=True):
    custom_fields = {'Item': [
        {
            "fieldname": "print_code",
            "fieldtype": "Data",
            "label": "PF Item Code",
        }
    ]}
    create_custom_fields(
        custom_fields, ignore_validate=frappe.flags.in_patch, update=update)


def make_custom_fields(update=True):
    custom_fields = {'Supplier': [
        {
            "fieldname": "supplier_process",
            "fieldtype": "Table",
            "label": "Supplier Process",
            "options": "Supplier_Process",
            "reqd": 1
        }
    ],
        'BOM': [
        {
            "fieldname": "process",
            "fieldtype": "Link",
            "label": "Process",
            "options": "Multi Process"
        }
    ],
        'Purchase Order': [
        {
            "fieldname": "dc",
            "fieldtype": "Link",
            "label": "DC",
            "options": "DC"
        },
        {
            "fieldname": "lot",
            "fieldtype": "Link",
            "label": "Lot",
            "options": "Lot Creation"
        }
    ]
    }
    create_custom_fields(
        custom_fields, ignore_validate=frappe.flags.in_patch, update=update)


@frappe.whitelist()
def get_ipd_item(doc):
    if isinstance(doc, string_types):
        doc = frappe._dict(json.loads(doc))

    doc['items'] = []

    lot = doc.get('lot')
    if not frappe.get_doc('Lot Creation', lot).docstatus:
        frappe.throw(_(f'Lot {lot} is not yet submitted'))

    dc_process = doc.get('process_1')
    apparelo_process = frappe.get_doc("Apparelo Process", dc_process)
    location = doc.get('location')

    lot_ipd = frappe.db.get_value(
        'Lot Creation', {'name': lot}, 'item_production_detail')
    ipd_bom_mapping = frappe.db.get_value(
        "IPD BOM Mapping", {'item_production_details': lot_ipd})
    boms = frappe.get_doc(
        'IPD BOM Mapping', ipd_bom_mapping).get_process_boms(dc_process)

    in_delivery_items = frappe.get_list("BOM Item", filters={'parent': [
                                        'in', boms]}, group_by='item_code', fields='item_code')
    from erpnext.stock.dashboard import item_dashboard
    dc_warehouse = frappe.db.get_value(
        "Warehouse", {'location': location, 'lot': lot, 'warehouse_type': 'Actual'}, 'name')
    items_to_be_sent = []
    for item in in_delivery_items:
        data = item_dashboard.get_data(
            item_code=item.item_code, warehouse=dc_warehouse)
        if len(data):
            item['available_quantity'] = data[0]['actual_qty']
            item_detail = frappe.get_doc('Item', item.item_code)
            item['primary_uom'] = item_detail.stock_uom
            item['secondary_uom'] = apparelo_process.in_secondary_uom
            item['pf_item_code'] = item_detail.print_code
            items_to_be_sent.append(item)
    return items_to_be_sent


@frappe.whitelist()
def get_expected_items_in_return(doc):
    if isinstance(doc, string_types):
        doc = frappe._dict(json.loads(doc))

    lot = doc.get('lot')
    dc_process = doc.get('process_1')
    apparelo_process = frappe.get_doc("Apparelo Process", dc_process)
    lot_ipd = frappe.db.get_value(
        'Lot Creation', {'name': lot}, 'item_production_detail')

    ipd_bom_mapping = frappe.db.get_value(
        'IPD BOM Mapping', {'item_production_details': lot_ipd})
    ipd_item_mapping = frappe.get_doc(
        "IPD Item Mapping", {'item_production_details': lot_ipd})
    boms = frappe.get_doc(
        'IPD BOM Mapping', ipd_bom_mapping).get_process_boms(dc_process)
    items_to_be_received = frappe.get_list('BOM', filters={
                                           'name': ['in', boms]}, group_by='item', fields=['item', 'name as bom'])

    receivable_list = {}
    item_mapping_validator = [x["item"] for x in frappe.get_list(
        "Item Mapping", {"parent": ipd_item_mapping.name, "process_1": dc_process}, "item")]
    items_to_be_received_with_removed_invalids_list = []
    for item_to_be_received in items_to_be_received:
        # Bringing in this condition for cutting to handle the combined parts.
        if item_to_be_received['item'] in item_mapping_validator:
            receivable_list[item_to_be_received['item']] = 0
            items_to_be_received_with_removed_invalids_list.append(
                item_to_be_received)

    items_to_be_received = items_to_be_received_with_removed_invalids_list

    lot_items = frappe.get_list('Lot Creation Plan Item', filters={
                                'parent': lot}, fields=['item_code', 'planned_qty', 'bom_no', 'stock_uom'])
    expect_return_items_at = frappe.db.get_value(
        'Warehouse', {'warehouse_name': f'{lot}-{doc.get("expect_return_items_at")}'}, 'name')
    # Invoke
    receivable_list = get_receivable_list_values(
        lot_items, receivable_list, expect_return_items_at)

    percentage_in_excess = frappe.db.get_value(
        'Lot Creation', lot, 'percentage')
    if percentage_in_excess:
        percentage_in_excess = (flt(percentage_in_excess) / 100)

    lot_ipd_doc = frappe.get_doc("Item Production Detail", lot_ipd)

    for item_to_be_received in items_to_be_received:
        item = frappe.get_doc('Item', item_to_be_received['item'])
        item_to_be_received['item_code'] = item_to_be_received['item']
        if item.stock_uom == 'Nos':
            item_to_be_received['qty'] = round(receivable_list[item_to_be_received['item']] + (
                receivable_list[item_to_be_received['item']] * percentage_in_excess))
        else:
            item_to_be_received['qty'] = receivable_list[item_to_be_received['item']] + (
                receivable_list[item_to_be_received['item']] * percentage_in_excess)

        ipd_process_index_of_item = -1
        for item_mappping in ipd_item_mapping.item_mapping:
            if item_mappping.item == item.item_code:
                ipd_process_index_of_item = item_mappping.ipd_process_index
                break
        if ipd_process_index_of_item == -1:
            frappe.throw(
                _(f"Item:{item.item_code} not found in IPD Item Mapping"))
        item_to_be_received['additional_parameters'] = get_additional_params(
            lot_ipd_doc.processes, ipd_process_index_of_item)

        item_to_be_received['pf_item_code'] = item.print_code if item.print_code != None and item.print_code != '' else item_to_be_received['item_code']
        item_to_be_received['uom'] = item.stock_uom
        item_to_be_received['secondary_uom'] = apparelo_process.out_secondary_uom

    return items_to_be_received


def get_receivable_list_values(lot_items, receivable_list, planned_warehouse=None):
    po_items = []
    company = get_default_company()
    for lot_item in lot_items:
        po_item = {}
        po_item['warehouse'] = planned_warehouse
        po_item['stock_uom'] = frappe.db.get_value(
            'Item', lot_item['item_code'], 'stock_uom')
        po_item['item_code'] = lot_item['item_code']
        po_item['planned_qty'] = lot_item['planned_qty']
        po_item['bom_no'] = lot_item['bom_no']
        po_items.append(po_item)

    # Using the production plan function doing the complete traversal of BOM while calculating the
    # required quantity in the receivable list. There is a scope to improve this if we can stop at
    # arriving the receivable list.
    while True:
        if len(po_items) > 0:
            input = {
                'company': company,
                'po_items': po_items
            }
            mr_items = get_items_for_material_requests(json.dumps(input))
        else:
            break
        po_items = []
        for mr_item in mr_items:
            if mr_item['item_code'] in receivable_list:
                receivable_list[mr_item['item_code']] += mr_item['quantity']

            bom_no = frappe.db.get_value(
                'Item', mr_item['item_code'], 'default_bom')
            po_item = {}
            if bom_no:
                po_item['bom_no'] = bom_no
                po_item['item_code'] = mr_item['item_code']
                po_item['planned_qty'] = mr_item['quantity']
                po_item['stock_uom'] = mr_item['stock_uom']
                po_item['warehouse'] = planned_warehouse
                po_items.append(po_item)

    return receivable_list


def get_additional_params(ipd_processes, ipd_process_index):
    ipd_process_array_index = int(ipd_process_index)-1
    if ipd_processes[ipd_process_array_index].idx == int(ipd_process_index):
        process_name = ipd_processes[ipd_process_array_index].process_name
        process_record = ipd_processes[ipd_process_array_index].process_record
        process_doc = frappe.get_doc(process_name, process_record)
        if process_doc.additional_information:
            additional_parameters_string = ''
            for info in process_doc.additional_information:
                additional_parameters_string += f'{info.parameter} : {info.value}\n'
            return additional_parameters_string
        else:
            return None
    else:
        frappe.throw(
            _("Unexpected error in getting additional params. IPD processes list was probably not sorted during fetch."))

@frappe.whitelist()
def dc_cloth_quantity(doc):
	if isinstance(doc, string_types):
		doc = frappe._dict(json.loads(doc))
	return_material_qty = {}
	column_list = set()
	column_dict = {}
	row_list = set()
	row_dict = {}
	return_material=doc.get('return_materials')
	for item in return_material:
		attribute_list = frappe.get_list("Item", filters={'name': ['in', item["item_code"]]}, fields=[
										"`tabItem Variant Attribute`.attribute", "`tabItem Variant Attribute`.attribute_value"])
		attribute_key = frappe.db.get_value('Item', {'name': item['item_code']},'variant_of')
		attribute_qty={}
		print(attribute_list)
		attribute_list=sorted(attribute_list,key=lambda attr: attr['attribute'])
		for attribute in attribute_list:
			if (len(attribute_qty)<2):
				if attribute['attribute'] == 'Apparelo Colour' :
					attribute_qty['colour'] = attribute['attribute_value']
					row_list.add(attribute['attribute_value'])
					row_dict ['colour'] = row_list
				if attribute['attribute'] == 'Apparelo Size':
					attribute_qty['size'] = attribute['attribute_value']
					column_list.add(attribute['attribute_value'])
					column_dict['size'] = column_list
				if attribute['attribute'] == 'Dia':
					attribute_qty['Dia'] = attribute['attribute_value']
					column_list.add(attribute['attribute_value'])
					column_dict['Dia'] = column_list
				if attribute['attribute'] == 'Knitting Type':
					attribute_qty['Knitting Type'] = attribute['attribute_value']
					row_list.add(attribute['attribute_value'])
					row_dict ['Knitting Type'] = row_list
			else:
				attribute_name_list=['Apparelo Colour','Apparelo Size']
				attribute_key += ' '
				if attribute['attribute'] not in attribute_name_list and attribute['attribute'] not in attribute_qty:
					attribute_key += attribute['attribute_value']
		attribute_qty['qty'] = item['qty']
		if attribute_key not in return_material_qty:
			return_material_qty[attribute_key] = [attribute_qty]
		else:
			return_material_qty[attribute_key].append(attribute_qty)
	html = ''
	for key,val in return_material_qty.items():
		html += f'<table class="table table-bordered"><tbody>{key}'
		html += html_generator(column_dict,row_dict,val)
		html += '</tbody></table>'
	return html


def html_generator(col,row,return_material_qty):
	print(col,row,return_material_qty)
	row_key = list(row.keys())[0]
	col_key = list(col.keys())[0]
	html_head = f'<tr><th>{col_key}/{row_key}</th>'
	html_body = ''
	html = ''
	for row_data in list(row[row_key]):
		html_head += f'<th>{row_data}</th>'
	html_head += '</tr>'
	row_list =[]
	for col_data in list(col[col_key]):
		sub_row_list = [0]*(len(list(row[row_key]))+1)
		sub_row_list[0] = col_data
		for row_data in list(row[row_key]):
			for items in return_material_qty:
				if ((items[col_key] == col_data) and (items[row_key] == row_data)):
					sub_row_list[list(row[row_key]).index(row_data) +1] = items['qty']
					break
		row_list.append(sub_row_list)
	for sub_row_data in row_list:
		html_body_data = ''
		if sum(map(int,sub_row_data[1:])) != 0:
			for sub_row_value in sub_row_data:
				html_body_data += f'<td>{sub_row_value}</td>'
		html_body += f'<tr>{html_body_data}</tr>'
		print(html_body)
	html += f'<tr>{html_head}</tr>{html_body}'
	return html
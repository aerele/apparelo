# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from apparelo.apparelo.doctype.ipd_item_mapping.ipd_item_mapping import ipd_item_mapping
from apparelo.apparelo.doctype.ipd_bom_mapping.ipd_bom_mapping import ipd_bom_mapping
class ItemProductionDetail(Document):

	def on_submit(self):
		ipd_list=self.create_process_details()
		ipd_item_mapping(ipd_list,self.name,self.item)
		ipd_bom_mapping(ipd_list,self.name,self.item)

	def create_process_details(self):
		ipd = []
		for process in self.processes:
			process_variants = {}
			if process.process_name == 'Knitting':
				process_variants['process'] = 'Knitting'
				process_variants['index']=process.idx
				if process.input_item:
					knitting_doc = frappe.get_doc('Knitting', process.process_record)
					variants = knitting_doc.create_variants([process.input_item])
					process_variants['variants'] = variants
					boms=knitting_doc.create_boms([process.input_item], variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)

				elif process.input_index:
					pass
				
				continue

			if process.process_name == 'Dyeing':
				process_variants['process'] = 'Dyeing'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Dyeing.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
							input_items.extend(pro['variants'])
					dyeing_doc = frappe.get_doc('Dyeing', process.process_record)
					variants = dyeing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = dyeing_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Steaming':
				process_variants['process'] = 'Steaming'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Steaming.create_variants as input items
					input_items = []
					for pro in ipd:
						# i pro['process'] == self.processes[int(process.input_index) - 1].process_name:
						if str(pro['index'])==process.input_index:
							input_items.extend(pro['variants'])
					steaming_doc = frappe.get_doc('Steaming', process.process_record)
					variants = steaming_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = steaming_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Compacting':
				process_variants['process'] = 'Compacting'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Compacting.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
						# if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					compacting_doc = frappe.get_doc('Compacting', process.process_record)
					variants = compacting_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = compacting_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Bleaching':
				process_variants['process'] = 'Bleaching'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Bleaching.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
						# if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					bleaching_doc = frappe.get_doc('Bleaching', process.process_record)
					variants = bleaching_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = bleaching_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Cutting':
				process_variants['process'] = 'Cutting'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Cutting.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
						# if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					cutting_doc = frappe.get_doc('Cutting', process.process_record)
					variants = cutting_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = cutting_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Piece Printing':
				process_variants['process'] = 'Piece Printing'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Piece Printing.create_variants as input items
					input_items = []
					for pro in ipd:
						index=self.processes[int(process.input_index) - 1]
						if str(pro['index'])==process.input_index:
						# if pro['process'] == index.process_name:
							input_items.extend(pro['variants'])
					piece_printing_doc = frappe.get_doc('Piece Printing', process.process_record)
					variants = piece_printing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = piece_printing_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Stitching':
				process_variants['process'] = 'Stitching'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Stitching.create_variants as input items
					input_items = []
					input_indexs = process.input_index.split(',')
					for pro in ipd:
						for input_index in input_indexs:
							if str(pro['index'])==input_index:
							# if pro['process'] == self.processes[int(input_index) - 1].process_name:
								input_items.extend(pro['variants'])
					stitching_doc = frappe.get_doc('Stitching', process.process_record)
					variants = stitching_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = stitching_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Label Fusing':
				process_variants['process'] = 'Label Fusing'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Label Fusing.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
						# if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					label_fusing_doc = frappe.get_doc('Label Fusing', process.process_record)
					variants = label_fusing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = label_fusing_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Checking':
				process_variants['process'] = 'Checking'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Checking.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
						# if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					checking_doc = frappe.get_doc('Checking', process.process_record)
					variants = checking_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = checking_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Ironing':
				process_variants['process'] = 'Ironing'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Ironing.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
						# if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					ironing_doc = frappe.get_doc('Ironing', process.process_record)
					variants = ironing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = ironing_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
			if process.process_name == 'Packing':
				index=process.idx
				process_variants['process'] = 'Packing'
				process_variants['index']=process.idx
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Packing.create_variants as input items
					input_items = []
					for pro in ipd:
						if str(pro['index'])==process.input_index:
						# if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					packing_doc = frappe.get_doc('Packing', process.process_record)
					variants = packing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = packing_doc.create_boms(input_items, variants)
					process_variants['BOM']=boms
					ipd.append(process_variants)
				continue
		return ipd
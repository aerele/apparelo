# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ItemProductionDetail(Document):

	def on_submit(self):
		self.create_process_details()

	def create_process_details(self):
		ipd = []
		for process in self.processes:
			process_variants = {}
			if process.process_name == 'Knitting':
				process_variants['process'] = 'Knitting'
				if process.input_item:
					knitting_doc = frappe.get_doc('Knitting', process.process_record)
					variants = knitting_doc.create_variants([process.input_item])
					process_variants['variants'] = variants
					boms=knitting_doc.create_boms([process.input_item], variants)
					ipd.append(process_variants)
				elif process.input_index:
					pass
				continue

			if process.process_name == 'Dyeing':
				process_variants['process'] = 'Dyeing'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Dyeing.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					dyeing_doc = frappe.get_doc('Dyeing', process.process_record)
					variants = dyeing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = dyeing_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Steaming':
				process_variants['process'] = 'Steaming'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Steaming.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					steaming_doc = frappe.get_doc('Steaming', process.process_record)
					variants = steaming_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = steaming_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Compacting':
				process_variants['process'] = 'Compacting'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Compacting.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					compacting_doc = frappe.get_doc('Compacting', process.process_record)
					variants = compacting_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = compacting_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Bleaching':
				process_variants['process'] = 'Bleaching'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Bleaching.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					bleaching_doc = frappe.get_doc('Bleaching', process.process_record)
					variants = bleaching_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = bleaching_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Cutting':
				process_variants['process'] = 'Cutting'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Cutting.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					cutting_doc = frappe.get_doc('Cutting', process.process_record)
					variants = cutting_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = cutting_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Piece Printing':
				process_variants['process'] = 'Piece Printing'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Piece Printing.create_variants as input items
					input_items = []
					for pro in ipd:
						index=self.processes[int(process.input_index) - 1]
						if pro['process'] == index.process_name:
							previous_doc = frappe.get_doc(index.process_name,index.process_record)
							input_items.extend(pro['variants'])
					piece_printing_doc = frappe.get_doc('Piece Printing', process.process_record)
					variants = piece_printing_doc.create_variants(input_items,previous_doc)
					process_variants['variants'] = variants
					boms = piece_printing_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Stitching':
				process_variants['process'] = 'Stitching'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Stitching.create_variants as input items
					input_items = []
					input_indexs = list(map(int,process.input_index.split(',')))
					for pro in ipd:
						for input_index in input_indexs:
							if pro['process'] == self.processes[int(input_index) - 1].process_name:
								input_items.extend(pro['variants'])
					stitching_doc = frappe.get_doc('Stitching', process.process_record)
					variants = stitching_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = stitching_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Label Fusing':
				process_variants['process'] = 'Label Fusing'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Label Fusing.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					label_fusing_doc = frappe.get_doc('Label Fusing', process.process_record)
					variants = label_fusing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = label_fusing_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Checking':
				process_variants['process'] = 'Checking'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Checking.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					checking_doc = frappe.get_doc('Checking', process.process_record)
					variants = checking_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = checking_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Ironing':
				process_variants['process'] = 'Ironing'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Ironing.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					ironing_doc = frappe.get_doc('Ironing', process.process_record)
					variants = ironing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = ironing_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
			if process.process_name == 'Packing':
				process_variants['process'] = 'Packing'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Packing.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					packing_doc = frappe.get_doc('Packing', process.process_record)
					variants = packing_doc.create_variants(input_items)
					process_variants['variants'] = variants
					boms = packing_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue
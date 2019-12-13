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
			if process.process_name == 'Stitching':
				process_variants['process'] = 'Stitching'
				if process.input_item:
					pass
				elif process.input_index:
					# Get the variants that were created out of that index
					# Pass them to the Stitching.create_variants as input items
					input_items = []
					for pro in ipd:
						if pro['process'] == self.processes[int(process.input_index) - 1].process_name:
							input_items.extend(pro['variants'])
					stitching_doc = frappe.get_doc('Stitching', process.process_record)
					variants = stitching_doc.create_variants(input_items)
					process_variants['variants'] = variants
					print(input_items)
					print("************************")
					boms = stitching_doc.create_boms(input_items, variants)
					ipd.append(process_variants)
				continue


# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloProcess(Document):
	pass
def create_apparelo_process(from_process=None,to_process=None):
	apparelo_process_list=[]
	apparelo_process=frappe.get_all("Apparelo Process",fields=['name'])
	for process_name in apparelo_process:
		apparelo_process_list.append(process_name.name)
	processes={'Knitting':['Bags','Roll'],'Dyeing':['Roll','Roll'],'Bleaching':['Roll','Roll'],'Compacting':['Roll','Roll'],'Steaming':['Roll','Roll'],'Roll Printing':['Roll','Roll'],'Cutting':['Roll','Kg'],'Stitching':['Kg','Kg'],'Piece Printing':['Kg','Kg'],'Label Fusing':['Kg','Kg'],'Checking':['Kg','Kg'],'Ironing':['Kg','Kg'],'Packing':['','']}
	for process in processes:
		if from_process and to_process:
			process_name=from_process+"-"+to_process
			if from_process==process:
				apparelo_process_doc=frappe.new_doc("Apparelo Process")
				apparelo_process_doc.apparelo_process=process_name
				apparelo_process_doc.in_secondary_uom=processes[process][1]
			if to_process==process:
				apparelo_process_doc.out_secondary_uom=processes[process][1]
				apparelo_process_doc.is_multi_process=1
				apparelo_process_doc.save()
		else:
			if not process in apparelo_process_list:
				apparelo_process_doc=frappe.new_doc("Apparelo Process")
				apparelo_process_doc.apparelo_process=process
				apparelo_process_doc.in_secondary_uom=processes[process][0]
				apparelo_process_doc.out_secondary_uom=processes[process][1]
				apparelo_process_doc.save()

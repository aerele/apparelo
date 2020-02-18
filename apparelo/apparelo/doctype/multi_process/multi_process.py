# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from apparelo.apparelo.doctype.apparelo_process.apparelo_process import create_apparelo_process
class MultiProcess(Document):
	def validate(self):
		create_apparelo_process(from_process=self.from_process,to_process=self.to_process)
		

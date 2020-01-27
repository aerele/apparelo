# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AdditionalParameters(Document):
	pass

def create_parameter():
	parameters = ['Loop Length','Gauge','GSM','Texture']
	for parameter in parameters:
		if not frappe.db.exists('Additional Parameters',parameter):
			doc = frappe.new_doc('Additional Parameters')
			doc.parameter = parameter
			doc.save()
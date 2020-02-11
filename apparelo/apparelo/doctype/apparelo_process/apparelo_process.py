# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AppareloProcess(Document):
	process={'Knitting':['Kg','Kg','Roll','Roll'],'Dyeing':['Kg','Kg','Roll','Roll'],'Bleaching':['Kg','Kg','Roll','Roll'],'Compacting':['Kg','Kg','Roll','Roll'],'Steaming':['Kg','Kg','Roll','Roll'],'Roll Printing':['Kg','Kg','Roll','Roll'],'Cutting':['Kg','Nos','Roll','Roll']}

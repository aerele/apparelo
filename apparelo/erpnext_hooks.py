# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals


def populate_pf_item_code(doc, action):
	if hasattr(doc, 'print_code') and action == 'validate':
		if not doc.print_code:
			doc.print_code = doc.item_code
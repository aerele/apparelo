# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

class TestKnitting(unittest.TestCase):
	pass

def test_variants_creation():
	from apparelo.apparelo.doctype.knitting.knitting import create_knittng_variants, create_knitting_boms
	input_items = []
	# TODO: This test can be used if the yarn mentioned below are created
	input_items.append(frappe.get_doc('Item', "Yarn-GREY-GREEN LABEL-34'S"))
	input_items.append(frappe.get_doc('Item', "Yarn-GREY-GREEN LABEL-30'S"))
	knitting_doc = frappe.get_doc('Knitting', 'Test Knitting')
	variants = create_knittng_variants(input_items, knitting_doc)
	create_knitting_boms(input_items, variants, knitting_doc)
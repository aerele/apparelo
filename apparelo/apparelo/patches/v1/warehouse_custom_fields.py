from __future__ import unicode_literals


def execute():
	from apparelo.apparelo.doctype.grn.warehouse_custom_fields import make_warehouse_custom_fields, create_warehouse_type
	create_warehouse_type()
	make_warehouse_custom_fields()
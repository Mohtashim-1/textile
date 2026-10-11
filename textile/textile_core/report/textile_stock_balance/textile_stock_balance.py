# Copyright (c) 2026, Mohtashim and contributors

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 180},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 120},
		{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
		{"label": _("Batch"), "fieldname": "batch_no", "fieldtype": "Link", "options": "Batch", "width": 140},
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
		{"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 80},
		{"label": _("Textile Lot/Roll"), "fieldname": "textile_ref", "fieldtype": "Data", "width": 160},
	]

	groups = ("Fibre", "Yarn", "Grey Fabric", "Finished Fabric", "Dyes", "Chemicals", "Textile")
	rows = frappe.db.sql(
		"""
		SELECT
			sle.item_code,
			i.item_name,
			i.item_group,
			sle.warehouse,
			sle.batch_no,
			SUM(sle.actual_qty) AS qty,
			i.stock_uom
		FROM `tabStock Ledger Entry` sle
		INNER JOIN `tabItem` i ON i.name = sle.item_code
		WHERE sle.is_cancelled = 0
			AND i.item_group IN %(groups)s
		GROUP BY sle.item_code, sle.warehouse, sle.batch_no, i.item_name, i.item_group, i.stock_uom
		HAVING SUM(sle.actual_qty) != 0
		ORDER BY i.item_group, sle.item_code, sle.warehouse
		""",
		{"groups": groups},
		as_dict=True,
	)

	for r in rows:
		ref = None
		if r.batch_no:
			ref = (
				frappe.db.get_value("Fibre Lot", {"batch_no": r.batch_no}, "name")
				or frappe.db.get_value("Yarn Lot", {"batch_no": r.batch_no}, "name")
				or frappe.db.get_value("Fabric Roll", {"batch_no": r.batch_no}, "name")
			)
		r["textile_ref"] = ref

	return columns, rows

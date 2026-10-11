# Copyright (c) 2026, Mohtashim and contributors

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{"label": _("Stock Entry"), "fieldname": "stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 140},
		{"label": _("Purpose"), "fieldname": "purpose", "fieldtype": "Data", "width": 110},
		{"label": _("Process Doc"), "fieldname": "process_doc", "fieldtype": "Data", "width": 160},
		{"label": _("Process Name"), "fieldname": "process_name", "fieldtype": "Dynamic Link", "options": "process_doc", "width": 160},
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 160},
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
		{"label": _("From WH"), "fieldname": "s_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
		{"label": _("To WH"), "fieldname": "t_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
		{"label": _("Batch"), "fieldname": "batch_no", "fieldtype": "Link", "options": "Batch", "width": 120},
	]

	# Map stock entries referenced from textile process docs
	refs = []
	for dt in (
		"Spinning Production Entry",
		"Weaving Production Entry",
		"Knitting Production Entry",
		"Dyeing Batch",
		"Fibre Lot",
	):
		for row in frappe.get_all(dt, fields=["name", "stock_entry"], filters={"stock_entry": ["is", "set"]}):
			refs.append({"process_doc": dt, "process_name": row.name, "stock_entry": row.stock_entry})

	if not refs:
		return columns, []

	se_names = [r["stock_entry"] for r in refs]
	ref_map = {r["stock_entry"]: r for r in refs}

	data = frappe.db.sql(
		"""
		SELECT
			se.posting_date,
			se.name AS stock_entry,
			se.purpose,
			sed.item_code,
			sed.qty,
			sed.s_warehouse,
			sed.t_warehouse,
			sed.batch_no
		FROM `tabStock Entry` se
		INNER JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
		WHERE se.docstatus = 1 AND se.name IN %(names)s
		ORDER BY se.posting_date, se.name
		""",
		{"names": se_names},
		as_dict=True,
	)

	for row in data:
		meta = ref_map.get(row.stock_entry) or {}
		row["process_doc"] = meta.get("process_doc")
		row["process_name"] = meta.get("process_name")

	return columns, data

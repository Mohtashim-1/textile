# Copyright (c) 2026, Mohtashim and contributors
"""Bridge Textile process docs to ERPNext Stock Entry / Item / Batch."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, nowdate


def get_company() -> str:
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		company = frappe.db.get_value("Company", {}, "name")
	if not company:
		frappe.throw(_("No Company found. Create a Company first."))
	return company


def get_uom(preferred: str = "Kg") -> str:
	for name in (preferred, "Kilogram", "Kg", "kg", "Meter", "Nos"):
		if name and frappe.db.exists("UOM", name):
			return name
	doc = frappe.get_doc({"doctype": "UOM", "uom_name": preferred or "Kg"})
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_item_group(name: str, parent: str | None = None, is_group: int = 0) -> str:
	if frappe.db.exists("Item Group", name):
		if is_group and not frappe.db.get_value("Item Group", name, "is_group"):
			frappe.db.set_value("Item Group", name, "is_group", 1)
		return name
	parent = parent or frappe.db.get_value("Item Group", {"is_group": 1}, "name")
	doc = frappe.get_doc(
		{
			"doctype": "Item Group",
			"item_group_name": name,
			"parent_item_group": parent,
			"is_group": is_group,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_warehouse(warehouse_name: str, company: str | None = None) -> str:
	company = company or get_company()
	abbr = frappe.get_cached_value("Company", company, "abbr")
	full = warehouse_name if " - " in warehouse_name else f"{warehouse_name} - {abbr}"
	if frappe.db.exists("Warehouse", full):
		return full
	parent = frappe.db.get_value("Warehouse", {"company": company, "is_group": 1}, "name")
	doc = frappe.get_doc(
		{
			"doctype": "Warehouse",
			"warehouse_name": warehouse_name,
			"company": company,
			"parent_warehouse": parent,
			"is_group": 0,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def textile_warehouses(company: str | None = None) -> dict[str, str]:
	company = company or get_company()
	return {
		"fibre": ensure_warehouse("Fibre Store", company),
		"yarn": ensure_warehouse("Yarn Store", company),
		"grey": ensure_warehouse("Grey Fabric", company),
		"finished": ensure_warehouse("Finished Fabric", company),
		"wip": ensure_warehouse("Work In Progress", company),
		"stores": ensure_warehouse("Stores", company),
		"chemical": ensure_warehouse("Dye Chemical Store", company),
	}


def ensure_item(
	item_code: str,
	*,
	item_group: str = "Textile",
	uom: str | None = None,
	has_batch: int = 1,
	item_name: str | None = None,
) -> str:
	if frappe.db.exists("Item", item_code):
		# ensure batch No if requested
		if has_batch and not frappe.db.get_value("Item", item_code, "has_batch_no"):
			frappe.db.set_value("Item", item_code, {"has_batch_no": 1, "create_new_batch": 1})
		return item_code

	ensure_item_group(item_group)
	uom = uom or get_uom("Kg")
	doc = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": item_code,
			"item_name": item_name or item_code,
			"item_group": item_group,
			"stock_uom": uom,
			"is_stock_item": 1,
			"include_item_in_manufacturing": 1,
			"has_batch_no": has_batch,
			"create_new_batch": has_batch,
			"is_purchase_item": 1,
			"is_sales_item": 1,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_batch(batch_id: str, item_code: str) -> str:
	if frappe.db.exists("Batch", batch_id):
		return batch_id
	doc = frappe.get_doc(
		{
			"doctype": "Batch",
			"batch_id": batch_id,
			"item": item_code,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def get_stock_balance(item_code: str, warehouse: str, batch_no: str | None = None) -> float:
	filters = {"item_code": item_code, "warehouse": warehouse}
	if batch_no:
		filters["batch_no"] = batch_no
	return flt(
		frappe.db.get_value(
			"Bin",
			{"item_code": item_code, "warehouse": warehouse},
			"actual_qty",
		)
		or 0
	)


def create_stock_entry(
	*,
	purpose: str,
	items: list[dict],
	company: str | None = None,
	posting_date: str | None = None,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	remarks: str | None = None,
) -> str:
	"""Create and submit a Stock Entry. items: dicts with item_code, qty, s_warehouse/t_warehouse, batch_no, is_finished_item."""
	company = company or get_company()
	se = frappe.new_doc("Stock Entry")
	se.company = company
	se.purpose = purpose
	se.stock_entry_type = purpose
	se.posting_date = posting_date or nowdate()
	se.set_posting_time = 1
	if remarks:
		se.remarks = remarks
	if reference_doctype and reference_name:
		se.textile_reference_type = reference_doctype if hasattr(se, "textile_reference_type") else None
		# store in remarks for traceability even without custom field
		se.remarks = (remarks or "") + f" | Ref: {reference_doctype} {reference_name}"

	for row in items:
		qty = flt(row.get("qty"))
		if qty <= 0:
			continue
		se.append(
			"items",
			{
				"item_code": row["item_code"],
				"qty": qty,
				"uom": row.get("uom") or frappe.db.get_value("Item", row["item_code"], "stock_uom"),
				"stock_uom": row.get("uom") or frappe.db.get_value("Item", row["item_code"], "stock_uom"),
				"conversion_factor": 1,
				"s_warehouse": row.get("s_warehouse"),
				"t_warehouse": row.get("t_warehouse"),
				"batch_no": row.get("batch_no"),
				"is_finished_item": row.get("is_finished_item") or 0,
				"basic_rate": flt(row.get("basic_rate") or 0),
			},
		)

	if not se.items:
		frappe.throw(_("No stock items to post for {0} {1}").format(reference_doctype, reference_name))

	se.insert(ignore_permissions=True)
	se.submit()
	return se.name


def material_receipt(
	item_code: str,
	qty: float,
	warehouse: str,
	batch_no: str | None = None,
	rate: float = 0,
	**ref,
) -> str:
	return create_stock_entry(
		purpose="Material Receipt",
		items=[
			{
				"item_code": item_code,
				"qty": qty,
				"t_warehouse": warehouse,
				"batch_no": batch_no,
				"basic_rate": rate or 100,
			}
		],
		**ref,
	)


def manufacture_entry(
	consume: list[dict],
	produce: dict,
	**ref,
) -> str:
	"""consume: [{item_code, qty, warehouse, batch_no}], produce: {item_code, qty, warehouse, batch_no, rate}."""
	items = []
	for c in consume:
		items.append(
			{
				"item_code": c["item_code"],
				"qty": c["qty"],
				"s_warehouse": c["warehouse"],
				"batch_no": c.get("batch_no"),
				"is_finished_item": 0,
			}
		)
	items.append(
		{
			"item_code": produce["item_code"],
			"qty": produce["qty"],
			"t_warehouse": produce["warehouse"],
			"batch_no": produce.get("batch_no"),
			"is_finished_item": 1,
			"basic_rate": produce.get("rate") or 0,
		}
	)
	return create_stock_entry(purpose="Manufacture", items=items, **ref)


def material_issue(item_code: str, qty: float, warehouse: str, batch_no: str | None = None, **ref) -> str:
	return create_stock_entry(
		purpose="Material Issue",
		items=[{"item_code": item_code, "qty": qty, "s_warehouse": warehouse, "batch_no": batch_no}],
		**ref,
	)


def cancel_stock_entry(stock_entry: str | None):
	if not stock_entry or not frappe.db.exists("Stock Entry", stock_entry):
		return
	doc = frappe.get_doc("Stock Entry", stock_entry)
	if doc.docstatus == 1:
		doc.cancel()


def item_code_for_fibre(fibre_type: str) -> str:
	return f"FIBRE-{frappe.scrub(fibre_type).upper()}"


def item_code_for_yarn(yarn_count: str, composition: str | None = None) -> str:
	base = f"YARN-{frappe.scrub(yarn_count or 'COUNT').upper()}"
	if composition:
		base += f"-{frappe.scrub(composition)[:20].upper()}"
	return base[:140]


def item_code_for_fabric(construction_name: str, stage: str = "GREY") -> str:
	return f"FAB-{stage}-{frappe.scrub(construction_name or 'FABRIC').upper()}"[:140]


def setup_textile_stock_masters(company: str | None = None) -> dict:
	"""Create warehouses, item groups, UOMs used by textile stock posts."""
	company = company or get_company()
	get_uom("Kg")
	if not frappe.db.exists("UOM", "Meter"):
		get_uom("Meter")

	# Required before Items can use has_batch_no
	if not frappe.db.get_single_value("Stock Settings", "enable_serial_and_batch_no_for_item"):
		frappe.db.set_single_value("Stock Settings", "enable_serial_and_batch_no_for_item", 1)

	ensure_item_group("Textile", is_group=1)
	ensure_item_group("Fibre", "Textile")
	ensure_item_group("Yarn", "Textile")
	ensure_item_group("Grey Fabric", "Textile")
	ensure_item_group("Finished Fabric", "Textile")
	ensure_item_group("Dyes", "Textile")
	ensure_item_group("Chemicals", "Textile")
	wh = textile_warehouses(company)
	return {"company": company, "warehouses": wh}

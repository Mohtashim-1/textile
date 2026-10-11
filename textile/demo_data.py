# Copyright (c) 2026, Mohtashim and contributors
"""Seed textile demo data for vertical walkthrough."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, flt, today


def ensure_roles_and_workspace():
	_ensure_role("Textile Manager")
	_ensure_workspace()


def _ensure_role(role: str):
	if not frappe.db.exists("Role", role):
		doc = frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1})
		doc.insert(ignore_permissions=True)


def _ensure_workspace():
	name = "Textile"
	content = [
		{"id": "hdr1", "type": "header", "data": {"text": "<span class='h4'>Textile Vertical</span>", "col": 12}},
		{"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Textile Machine", "col": 3}},
		{"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Fibre Lot", "col": 3}},
		{"id": "s3", "type": "shortcut", "data": {"shortcut_name": "Mixing Plan", "col": 3}},
		{"id": "s4", "type": "shortcut", "data": {"shortcut_name": "Spinning Production Entry", "col": 3}},
		{"id": "s5", "type": "shortcut", "data": {"shortcut_name": "Yarn Lot", "col": 3}},
		{"id": "s6", "type": "shortcut", "data": {"shortcut_name": "Warp Beam", "col": 3}},
		{"id": "s7", "type": "shortcut", "data": {"shortcut_name": "Weaving Production Entry", "col": 3}},
		{"id": "s8", "type": "shortcut", "data": {"shortcut_name": "Knitting Production Entry", "col": 3}},
		{"id": "s9", "type": "shortcut", "data": {"shortcut_name": "Fabric Roll", "col": 3}},
		{"id": "s10", "type": "shortcut", "data": {"shortcut_name": "Shade", "col": 3}},
		{"id": "s11", "type": "shortcut", "data": {"shortcut_name": "Dyeing Batch", "col": 3}},
		{"id": "s12", "type": "shortcut", "data": {"shortcut_name": "Buyer Programme", "col": 3}},
	]
	shortcuts = [
		{"label": "Textile Machine", "link_to": "Textile Machine", "type": "DocType"},
		{"label": "Fibre Lot", "link_to": "Fibre Lot", "type": "DocType"},
		{"label": "Mixing Plan", "link_to": "Mixing Plan", "type": "DocType"},
		{"label": "Spinning Production Entry", "link_to": "Spinning Production Entry", "type": "DocType"},
		{"label": "Yarn Lot", "link_to": "Yarn Lot", "type": "DocType"},
		{"label": "Warp Beam", "link_to": "Warp Beam", "type": "DocType"},
		{"label": "Weaving Production Entry", "link_to": "Weaving Production Entry", "type": "DocType"},
		{"label": "Knitting Production Entry", "link_to": "Knitting Production Entry", "type": "DocType"},
		{"label": "Fabric Roll", "link_to": "Fabric Roll", "type": "DocType"},
		{"label": "Shade", "link_to": "Shade", "type": "DocType"},
		{"label": "Dyeing Batch", "link_to": "Dyeing Batch", "type": "DocType"},
		{"label": "Buyer Programme", "link_to": "Buyer Programme", "type": "DocType"},
	]
	links = [
		{"label": "Core", "type": "Card Break"},
		{"label": "Textile Machine", "link_to": "Textile Machine", "link_type": "DocType", "type": "Link"},
		{"label": "Shade", "link_to": "Shade", "link_type": "DocType", "type": "Link"},
		{"label": "Fabric Construction", "link_to": "Fabric Construction", "link_type": "DocType", "type": "Link"},
		{"label": "Fibre Lot", "link_to": "Fibre Lot", "link_type": "DocType", "type": "Link"},
		{"label": "Yarn Lot", "link_to": "Yarn Lot", "link_type": "DocType", "type": "Link"},
		{"label": "Fabric Roll", "link_to": "Fabric Roll", "link_type": "DocType", "type": "Link"},
		{"label": "Spinning", "type": "Card Break"},
		{"label": "Mixing Plan", "link_to": "Mixing Plan", "link_type": "DocType", "type": "Link"},
		{"label": "Spinning Production Entry", "link_to": "Spinning Production Entry", "link_type": "DocType", "type": "Link"},
		{"label": "Weaving", "type": "Card Break"},
		{"label": "Warp Beam", "link_to": "Warp Beam", "link_type": "DocType", "type": "Link"},
		{"label": "Weaving Production Entry", "link_to": "Weaving Production Entry", "link_type": "DocType", "type": "Link"},
		{"label": "Fabric Inspection", "link_to": "Fabric Inspection", "link_type": "DocType", "type": "Link"},
		{"label": "Knitting", "type": "Card Break"},
		{"label": "Knitting Programme", "link_to": "Knitting Programme", "link_type": "DocType", "type": "Link"},
		{"label": "Knitting Production Entry", "link_to": "Knitting Production Entry", "link_type": "DocType", "type": "Link"},
		{"label": "Dyeing & Finishing", "type": "Card Break"},
		{"label": "Dye Recipe", "link_to": "Dye Recipe", "link_type": "DocType", "type": "Link"},
		{"label": "Dyeing Batch", "link_to": "Dyeing Batch", "link_type": "DocType", "type": "Link"},
		{"label": "Batch Test Result", "link_to": "Batch Test Result", "link_type": "DocType", "type": "Link"},
		{"label": "Sales", "type": "Card Break"},
		{"label": "Buyer Programme", "link_to": "Buyer Programme", "link_type": "DocType", "type": "Link"},
	]

	values = {
		"label": name,
		"title": name,
		"module": "Textile Core",
		"public": 1,
		"is_hidden": 0,
		"type": "Workspace",
		"icon": "organization",
		"content": frappe.as_json(content),
		"shortcuts": shortcuts,
		"links": links,
	}
	if frappe.db.exists("Workspace", name):
		doc = frappe.get_doc("Workspace", name)
		doc.update(values)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({"doctype": "Workspace", **values, "name": name})
		doc.insert(ignore_permissions=True)


@frappe.whitelist()
def create_demo_data(force: int = 0):
	"""Create end-to-end textile demo: fibre → yarn → grey → dyed → programme."""
	frappe.only_for(("System Manager", "Textile Manager"))
	force = int(force or 0)
	ensure_roles_and_workspace()

	if frappe.db.exists("Buyer Programme", {"programme_name": "DEMO-EXPORT-POLO"}) and not force:
		return {
			"skipped": True,
			"message": _("Demo data already exists. Pass force=1 to recreate."),
		}

	if force:
		_cleanup()

	company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
		"Company", {}, "name"
	)
	result = {"company": company}

	# Settings
	settings = frappe.get_single("Textile Settings")
	settings.enable_spinning = 1
	settings.enable_weaving = 1
	settings.enable_knitting = 1
	settings.enable_dyeing = 1
	settings.default_company = company
	kg = frappe.db.exists("UOM", "Kg") or frappe.db.exists("UOM", "kg")
	meter = frappe.db.exists("UOM", "Meter") or frappe.db.exists("UOM", "Metre")
	if kg:
		settings.weight_uom = kg
	if meter:
		settings.length_uom = meter
	settings.save(ignore_permissions=True)

	buyer = _ensure_customer("Nexora Apparel Buyer")
	supplier = _ensure_supplier("Sindh Cotton Mills")
	wh = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")

	# Machines
	machines = {}
	for name, dept, mtype in [
		("Card-01", "Spinning", "Card"),
		("RF-12", "Spinning", "Ring Frame"),
		("Loom-05", "Weaving", "Loom"),
		("Knit-03", "Knitting", "Knitting"),
		("Jet-02", "Dyeing", "Jet"),
	]:
		machines[name] = _ensure_machine(name, dept, mtype, wh)

	# Construction + shade
	const_woven = _ensure_doc(
		"Fabric Construction",
		{"construction_name": "30x30 76x68 Poplin"},
		{
			"process_type": "Woven",
			"weave_type": "Plain",
			"epi": 76,
			"ppi": 68,
			"gsm": 120,
			"width_inch": 58,
			"warp_count": "30s",
			"weft_count": "30s",
			"composition": "100% Cotton",
		},
	)
	const_knit = _ensure_doc(
		"Fabric Construction",
		{"construction_name": "Single Jersey 180 GSM"},
		{
			"process_type": "Knitted",
			"weave_type": "Jersey",
			"gsm": 180,
			"width_inch": 72,
			"composition": "100% Cotton",
		},
	)
	shade = _ensure_doc(
		"Shade",
		{"shade_code": "NVY-210"},
		{
			"shade_name": "Navy Blue 210",
			"buyer": buyer,
			"color": "Navy",
			"status": "Approved",
			"approval_date": today(),
		},
	)

	# Fibre lots
	fibre1 = frappe.get_doc(
		{
			"doctype": "Fibre Lot",
			"lot_no": "CTN-LOT-1001",
			"fibre_type": "Cotton",
			"grade": "Shankar-6",
			"supplier": supplier,
			"staple_length": 28.5,
			"micronaire": 4.2,
			"qty_kg": 5000,
			"warehouse": wh,
			"status": "Available",
		}
	).insert(ignore_permissions=True)
	fibre2 = frappe.get_doc(
		{
			"doctype": "Fibre Lot",
			"lot_no": "PSY-LOT-44",
			"fibre_type": "Polyester",
			"grade": "1.2D",
			"supplier": supplier,
			"qty_kg": 2000,
			"warehouse": wh,
			"status": "Available",
		}
	).insert(ignore_permissions=True)

	# Mixing
	mix = frappe.get_doc(
		{
			"doctype": "Mixing Plan",
			"plan_date": today(),
			"target_count": "30s Ne",
			"blend_name": "C60/P40 Demo Blend",
			"total_qty_kg": 1000,
			"status": "Approved",
			"fibres": [
				{"fibre_lot": fibre1.name, "ratio_percent": 60, "qty_kg": 600},
				{"fibre_lot": fibre2.name, "ratio_percent": 40, "qty_kg": 400},
			],
		}
	).insert(ignore_permissions=True)
	mix.submit()

	yarn = frappe.get_doc(
		{
			"doctype": "Yarn Lot",
			"lot_no": "YN-30s-DEMO-01",
			"yarn_count": "30s",
			"count_system": "Ne",
			"twist": 18.5,
			"ply": 1,
			"composition": "60% Cotton / 40% Polyester",
			"qty_kg": 920,
			"cones": 1840,
			"warehouse": wh,
			"source_process": "Spinning",
			"status": "Available",
		}
	).insert(ignore_permissions=True)

	spe = frappe.get_doc(
		{
			"doctype": "Spinning Production Entry",
			"posting_date": today(),
			"shift": "A",
			"process_stage": "Ring Frame",
			"machine": machines["RF-12"],
			"mixing_plan": mix.name,
			"yarn_count": "30s",
			"input_qty_kg": 1000,
			"output_qty_kg": 920,
			"waste_qty_kg": 80,
			"yield_percent": 92,
			"spindle_efficiency": 88.5,
			"yarn_lot": yarn.name,
		}
	).insert(ignore_permissions=True)
	spe.submit()

	beam = frappe.get_doc(
		{
			"doctype": "Warp Beam",
			"beam_no": "BEAM-DEMO-01",
			"construction": const_woven,
			"yarn_lot": yarn.name,
			"ends": 4200,
			"length_meter": 2500,
			"size_pickup_percent": 12,
			"sizing_recipe": "PVA + Starch demo recipe",
			"status": "On Loom",
			"loom": machines["Loom-05"],
		}
	).insert(ignore_permissions=True)

	grey_roll = frappe.get_doc(
		{
			"doctype": "Fabric Roll",
			"roll_no": "GR-1001",
			"barcode": "QR-GR-1001",
			"stage": "Grey",
			"process_type": "Woven",
			"construction": const_woven,
			"qty_meter": 1200,
			"qty_kg": 144,
			"gsm": 120,
			"width_inch": 58,
			"grade": "A",
			"warehouse": wh,
			"status": "Available",
		}
	).insert(ignore_permissions=True)

	wpe = frappe.get_doc(
		{
			"doctype": "Weaving Production Entry",
			"posting_date": today(),
			"shift": "A",
			"loom": machines["Loom-05"],
			"warp_beam": beam.name,
			"construction": const_woven,
			"picks": 180000,
			"rpm": 620,
			"efficiency_percent": 86,
			"downtime_minutes": 35,
			"output_meter": 1200,
			"output_kg": 144,
			"grey_roll": grey_roll.name,
		}
	).insert(ignore_permissions=True)
	wpe.submit()

	insp = frappe.get_doc(
		{
			"doctype": "Fabric Inspection",
			"inspection_date": today(),
			"fabric_roll": grey_roll.name,
			"inspection_system": "4 Point",
			"points": 12,
			"grade": "A",
			"defects": "Minor weft bars at 220m",
		}
	).insert(ignore_permissions=True)
	insp.submit()

	# Knitting side
	kp = frappe.get_doc(
		{
			"doctype": "Knitting Programme",
			"programme_date": today(),
			"buyer": buyer,
			"style": "Polo Basic",
			"colour": "Navy",
			"construction": const_knit,
			"order_qty_kg": 500,
			"status": "In Progress",
		}
	).insert(ignore_permissions=True)

	knit_roll = frappe.get_doc(
		{
			"doctype": "Fabric Roll",
			"roll_no": "KR-501",
			"barcode": "QR-KR-501",
			"stage": "Grey",
			"process_type": "Knitted",
			"construction": const_knit,
			"qty_kg": 48,
			"gsm": 180,
			"grade": "A",
			"warehouse": wh,
			"status": "Available",
		}
	).insert(ignore_permissions=True)

	kpe = frappe.get_doc(
		{
			"doctype": "Knitting Production Entry",
			"posting_date": today(),
			"shift": "B",
			"machine": machines["Knit-03"],
			"programme": kp.name,
			"yarn_lot": yarn.name,
			"yarn_issued_kg": 50,
			"fabric_produced_kg": 48,
			"waste_kg": 2,
			"wastage_percent": 4,
			"grey_roll": knit_roll.name,
		}
	).insert(ignore_permissions=True)
	kpe.submit()

	# Dyeing
	item_dye = _ensure_item("Reactive Dye Navy", "Dyes")
	item_chem = _ensure_item("Salt Glauber", "Chemicals")
	recipe = frappe.get_doc(
		{
			"doctype": "Dye Recipe",
			"recipe_name": "Navy Exhaust Demo",
			"shade": shade,
			"dyeing_process": "Fabric Dyeing",
			"liquor_ratio": "1:8",
			"status": "Approved",
			"items": [
				{"item_code": item_dye, "item_group": "Dye", "qty": 2.5, "uom": "Kg", "percent_owl": 2.5},
				{"item_code": item_chem, "item_group": "Chemical", "qty": 40, "uom": "Kg"},
			],
		}
	).insert(ignore_permissions=True)

	finished = frappe.get_doc(
		{
			"doctype": "Fabric Roll",
			"roll_no": "FR-NAVY-01",
			"barcode": "QR-FR-NAVY-01",
			"stage": "Finished",
			"process_type": "Knitted",
			"construction": const_knit,
			"shade": shade,
			"qty_kg": 45.5,
			"gsm": 180,
			"grade": "A",
			"warehouse": wh,
			"status": "Available",
		}
	).insert(ignore_permissions=True)

	batch = frappe.get_doc(
		{
			"doctype": "Dyeing Batch",
			"batch_date": today(),
			"shade": shade,
			"recipe": recipe.name,
			"machine": machines["Jet-02"],
			"input_type": "Grey Fabric",
			"input_qty_kg": 48,
			"output_qty_kg": 45.5,
			"process_loss_percent": 5.2,
			"pre_treatment": 1,
			"dyeing_done": 1,
			"washing_done": 1,
			"finishing_done": 1,
			"shade_approved": 1,
			"status": "Completed",
			"water_m3": 3.2,
			"steam_kg": 180,
			"power_kwh": 95,
			"dye_chemical_cost": 12500,
			"utility_cost": 4200,
			"total_cost": 16700,
			"cost_per_kg": 367.03,
			"input_roll": knit_roll.name,
			"output_roll": finished.name,
		}
	).insert(ignore_permissions=True)
	batch.submit()

	frappe.get_doc(
		{
			"doctype": "Batch Test Result",
			"test_date": today(),
			"dyeing_batch": batch.name,
			"shrinkage_percent": 3.5,
			"colour_fastness": "4-5",
			"gsm": 180,
			"result": "Pass",
		}
	).insert(ignore_permissions=True)

	programme = frappe.get_doc(
		{
			"doctype": "Buyer Programme",
			"buyer": buyer,
			"programme_name": "DEMO-EXPORT-POLO",
			"order_date": today(),
			"delivery_date": add_days(today(), 30),
			"construction": const_knit,
			"shade": shade,
			"order_qty": 500,
			"uom": "Kg",
			"status": "In Production",
			"export_docs": "LC: DEMO-LC-7781 | Packing list pending",
		}
	).insert(ignore_permissions=True)

	frappe.db.set_value("Fabric Roll", finished.name, "buyer_programme", programme.name)
	frappe.db.set_value("Knitting Programme", kp.name, "buyer_programme", programme.name)

	frappe.db.commit()
	result.update(
		{
			"buyer": buyer,
			"mixing_plan": mix.name,
			"yarn_lot": yarn.name,
			"grey_roll": grey_roll.name,
			"knit_roll": knit_roll.name,
			"dyeing_batch": batch.name,
			"finished_roll": finished.name,
			"buyer_programme": programme.name,
			"message": "Textile demo data created",
		}
	)
	return result


def _cleanup():
	for dt in [
		"Batch Test Result",
		"Dyeing Batch",
		"Dye Recipe",
		"Fabric Inspection",
		"Weaving Production Entry",
		"Knitting Production Entry",
		"Spinning Production Entry",
		"Warp Beam",
		"Knitting Programme",
		"Buyer Programme",
		"Fabric Roll",
		"Yarn Lot",
		"Mixing Plan",
		"Fibre Lot",
	]:
		for name in frappe.get_all(dt, pluck="name"):
			try:
				doc = frappe.get_doc(dt, name)
				if getattr(doc, "docstatus", 0) == 1:
					doc.cancel()
				frappe.delete_doc(dt, name, force=1, ignore_permissions=True)
			except Exception:
				frappe.db.delete(dt, {"name": name})
	frappe.db.commit()


def _ensure_customer(name):
	if frappe.db.exists("Customer", name):
		return name
	cg = (
		frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		or frappe.db.get_value("Customer Group", {}, "name")
	)
	territory = (
		frappe.db.get_value("Territory", {"is_group": 0}, "name")
		or frappe.db.get_value("Territory", {}, "name")
	)
	doc = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": name,
			"customer_type": "Company",
			"customer_group": cg,
			"territory": territory,
		}
	).insert(ignore_permissions=True)
	return doc.name


def _ensure_supplier(name):
	if frappe.db.exists("Supplier", name):
		return name
	sg = (
		frappe.db.get_value("Supplier Group", {"is_group": 0}, "name")
		or frappe.db.get_value("Supplier Group", {}, "name")
	)
	doc = frappe.get_doc(
		{
			"doctype": "Supplier",
			"supplier_name": name,
			"supplier_group": sg,
		}
	).insert(ignore_permissions=True)
	return doc.name


def _ensure_machine(name, department, machine_type, warehouse=None):
	existing = frappe.db.get_value("Textile Machine", {"machine_name": name}, "name")
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Textile Machine",
			"machine_name": name,
			"department": department,
			"machine_type": machine_type,
			"status": "Active",
			"warehouse": warehouse,
			"spindles": 480 if machine_type == "Ring Frame" else 0,
			"rpm": 620 if machine_type == "Loom" else 0,
			"gauge": 24 if machine_type == "Knitting" else 0,
			"diameter": 30 if machine_type == "Knitting" else 0,
		}
	).insert(ignore_permissions=True)
	return doc.name


def _ensure_doc(doctype, filters, values):
	name = frappe.db.get_value(doctype, filters, "name")
	if name:
		return name
	doc = frappe.get_doc({"doctype": doctype, **filters, **values}).insert(ignore_permissions=True)
	return doc.name


def _ensure_item(item_code, group_name):
	parent = (
		frappe.db.get_value("Item Group", {"is_group": 1}, "name")
		or frappe.db.get_value("Item Group", {}, "name")
	)
	if not frappe.db.exists("Item Group", group_name):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": group_name,
				"parent_item_group": parent,
				"is_group": 0,
			}
		).insert(ignore_permissions=True)
	if frappe.db.exists("Item", item_code):
		return item_code
	uom = frappe.db.exists("UOM", "Kg") or frappe.db.get_value("UOM", {}, "name")
	if not uom:
		uom_doc = frappe.get_doc({"doctype": "UOM", "uom_name": "Kg"}).insert(ignore_permissions=True)
		uom = uom_doc.name
	doc = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": item_code,
			"item_name": item_code,
			"item_group": group_name,
			"stock_uom": uom,
			"is_stock_item": 1,
			"include_item_in_manufacturing": 1,
		}
	).insert(ignore_permissions=True)
	return doc.name

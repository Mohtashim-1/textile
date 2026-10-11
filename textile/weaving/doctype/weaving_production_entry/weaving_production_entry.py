# Copyright (c) 2026, Mohtashim and contributors
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from textile.erpnext_stock import (
	cancel_stock_entry,
	ensure_batch,
	ensure_item,
	item_code_for_fabric,
	manufacture_entry,
	setup_textile_stock_masters,
	textile_warehouses,
)


class WeavingProductionEntry(Document):
	def on_submit(self):
		self.post_stock()

	def on_cancel(self):
		cancel_stock_entry(self.stock_entry)
		frappe.db.set_value(self.doctype, self.name, {"stock_entry": None, "stock_posted": 0})

	def post_stock(self):
		if self.stock_posted and self.stock_entry:
			return
		qty = flt(self.output_kg) or flt(self.output_meter)
		if qty <= 0:
			frappe.throw(_("Output qty is required to post stock"))

		setup_textile_stock_masters()
		wh = textile_warehouses()
		consume = []

		if self.warp_beam:
			beam = frappe.get_doc("Warp Beam", self.warp_beam)
			if beam.yarn_lot:
				yarn = frappe.get_doc("Yarn Lot", beam.yarn_lot)
				if not yarn.item_code:
					frappe.throw(_("Yarn Lot {0} has no Item. Post spinning stock first.").format(yarn.name))
				# consume yarn proportional to output kg, fallback 10% of beam yarn estimate
				yarn_qty = flt(self.output_kg) or (flt(self.output_meter) * 0.12)
				consume.append(
					{
						"item_code": yarn.item_code,
						"qty": yarn_qty,
						"warehouse": yarn.warehouse or wh["yarn"],
						"batch_no": yarn.batch_no,
					}
				)

		if not consume:
			frappe.throw(_("Warp Beam with Yarn Lot is required to consume yarn stock"))

		const_name = None
		if self.construction:
			const_name = frappe.db.get_value("Fabric Construction", self.construction, "construction_name")
		fab_item = ensure_item(
			item_code_for_fabric(const_name or self.construction or "WOVEN", "GREY"),
			item_group="Grey Fabric",
			item_name=f"Grey {const_name or 'Woven'}",
			uom="Kg" if flt(self.output_kg) else "Meter",
		)

		roll = None
		if self.grey_roll:
			roll = frappe.get_doc("Fabric Roll", self.grey_roll)
		batch_id = (roll.roll_no if roll else None) or f"GR-{self.name}"
		batch = ensure_batch(batch_id, fab_item)
		prod_qty = flt(self.output_kg) or flt(self.output_meter)

		se = manufacture_entry(
			consume=consume,
			produce={
				"item_code": fab_item,
				"qty": prod_qty,
				"warehouse": wh["grey"],
				"batch_no": batch,
				"rate": 220,
			},
			posting_date=self.posting_date,
			reference_doctype=self.doctype,
			reference_name=self.name,
			remarks=f"Weaving production {self.name}",
		)

		if roll:
			frappe.db.set_value(
				"Fabric Roll",
				roll.name,
				{
					"item_code": fab_item,
					"batch_no": batch,
					"warehouse": wh["grey"],
					"stock_entry": se,
					"stage": "Grey",
				},
				update_modified=False,
			)

		self.db_set({"stock_entry": se, "stock_posted": 1})

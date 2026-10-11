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
	item_code_for_yarn,
	manufacture_entry,
	setup_textile_stock_masters,
	textile_warehouses,
)


class SpinningProductionEntry(Document):
	def validate(self):
		if flt(self.input_qty_kg):
			self.yield_percent = flt(self.output_qty_kg) / flt(self.input_qty_kg) * 100
		if self.waste_qty_kg in (None, "") and flt(self.input_qty_kg):
			self.waste_qty_kg = flt(self.input_qty_kg) - flt(self.output_qty_kg)

	def on_submit(self):
		self.post_stock()

	def on_cancel(self):
		cancel_stock_entry(self.stock_entry)
		frappe.db.set_value(self.doctype, self.name, {"stock_entry": None, "stock_posted": 0})

	def post_stock(self):
		if self.stock_posted and self.stock_entry:
			return
		if flt(self.output_qty_kg) <= 0:
			frappe.throw(_("Output Qty (Kg) is required to post stock"))

		setup_textile_stock_masters()
		wh = textile_warehouses()
		consume = []

		if self.mixing_plan:
			plan = frappe.get_doc("Mixing Plan", self.mixing_plan)
			total_ratio = sum(flt(r.ratio_percent) for r in plan.fibres) or 100
			for row in plan.fibres:
				fibre = frappe.get_doc("Fibre Lot", row.fibre_lot)
				if not fibre.item_code:
					fibre.post_opening_stock()
					fibre.reload()
				qty = flt(self.input_qty_kg) * flt(row.ratio_percent) / total_ratio
				if qty <= 0:
					continue
				consume.append(
					{
						"item_code": fibre.item_code,
						"qty": qty,
						"warehouse": fibre.warehouse or wh["fibre"],
						"batch_no": fibre.batch_no,
					}
				)

		if not consume:
			frappe.throw(_("Link a Mixing Plan with Fibre Lots so raw material can be consumed"))

		yarn_lot = None
		if self.yarn_lot:
			yarn_lot = frappe.get_doc("Yarn Lot", self.yarn_lot)
		composition = yarn_lot.composition if yarn_lot else None
		yarn_count = self.yarn_count or (yarn_lot.yarn_count if yarn_lot else "COUNT")
		yarn_item = ensure_item(
			item_code_for_yarn(yarn_count, composition),
			item_group="Yarn",
			item_name=f"Yarn {yarn_count}",
		)
		batch_id = (yarn_lot.lot_no if yarn_lot else None) or f"YN-{self.name}"
		batch = ensure_batch(batch_id, yarn_item)

		se = manufacture_entry(
			consume=consume,
			produce={
				"item_code": yarn_item,
				"qty": flt(self.output_qty_kg),
				"warehouse": wh["yarn"],
				"batch_no": batch,
				"rate": 180,
			},
			posting_date=self.posting_date,
			reference_doctype=self.doctype,
			reference_name=self.name,
			remarks=f"Spinning {self.process_stage} {self.name}",
		)

		if yarn_lot:
			frappe.db.set_value(
				"Yarn Lot",
				yarn_lot.name,
				{
					"item_code": yarn_item,
					"batch_no": batch,
					"warehouse": wh["yarn"],
					"stock_entry": se,
				},
				update_modified=False,
			)

		self.db_set({"stock_entry": se, "stock_posted": 1})

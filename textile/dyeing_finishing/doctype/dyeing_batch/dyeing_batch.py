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
	material_receipt,
	setup_textile_stock_masters,
	textile_warehouses,
)


class DyeingBatch(Document):
	def validate(self):
		self.total_cost = flt(self.dye_chemical_cost) + flt(self.utility_cost)
		if flt(self.input_qty_kg):
			self.process_loss_percent = (
				(flt(self.input_qty_kg) - flt(self.output_qty_kg)) / flt(self.input_qty_kg) * 100
			)
		if flt(self.output_qty_kg):
			self.cost_per_kg = flt(self.total_cost) / flt(self.output_qty_kg)

	def on_submit(self):
		self.post_stock()

	def on_cancel(self):
		cancel_stock_entry(self.stock_entry)
		frappe.db.set_value(self.doctype, self.name, {"stock_entry": None, "stock_posted": 0})

	def post_stock(self):
		if self.stock_posted and self.stock_entry:
			return
		if flt(self.input_qty_kg) <= 0 or flt(self.output_qty_kg) <= 0:
			frappe.throw(_("Input and Output qty (Kg) are required to post stock"))
		if not self.input_roll:
			frappe.throw(_("Input Fabric Roll is required"))

		setup_textile_stock_masters()
		wh = textile_warehouses()
		consume = []

		in_roll = frappe.get_doc("Fabric Roll", self.input_roll)
		if not in_roll.item_code:
			frappe.throw(_("Input roll {0} has no Item. Post weaving/knitting stock first.").format(in_roll.name))
		consume.append(
			{
				"item_code": in_roll.item_code,
				"qty": flt(self.input_qty_kg),
				"warehouse": in_roll.warehouse or wh["grey"],
				"batch_no": in_roll.batch_no,
			}
		)

		# dye/chemical consumption from recipe
		if self.recipe:
			recipe = frappe.get_doc("Dye Recipe", self.recipe)
			for row in recipe.items:
				if not row.item_code or flt(row.qty) <= 0:
					continue
				# ensure chemicals are in stock (demo receipt if empty)
				bal = flt(
					frappe.db.get_value(
						"Bin",
						{"item_code": row.item_code, "warehouse": wh["chemical"]},
						"actual_qty",
					)
				)
				need = flt(row.qty)
				if bal < need:
					material_receipt(
						row.item_code,
						need - bal + 1,
						wh["chemical"],
						rate=50,
						posting_date=self.batch_date,
						reference_doctype=self.doctype,
						reference_name=self.name,
						remarks=f"Auto receipt for dye/chemical {row.item_code}",
					)
				consume.append(
					{
						"item_code": row.item_code,
						"qty": need,
						"warehouse": wh["chemical"],
					}
				)

		const_name = None
		if in_roll.construction:
			const_name = frappe.db.get_value("Fabric Construction", in_roll.construction, "construction_name")
		shade_code = frappe.db.get_value("Shade", self.shade, "shade_code") if self.shade else "SHADE"
		fg_item = ensure_item(
			item_code_for_fabric(f"{const_name or 'FAB'}-{shade_code}", "FIN"),
			item_group="Finished Fabric",
			item_name=f"Finished {shade_code}",
		)

		out_roll = frappe.get_doc("Fabric Roll", self.output_roll) if self.output_roll else None
		batch = ensure_batch((out_roll.roll_no if out_roll else None) or f"FR-{self.name}", fg_item)

		se = manufacture_entry(
			consume=consume,
			produce={
				"item_code": fg_item,
				"qty": flt(self.output_qty_kg),
				"warehouse": wh["finished"],
				"batch_no": batch,
				"rate": flt(self.cost_per_kg) or 350,
			},
			posting_date=self.batch_date,
			reference_doctype=self.doctype,
			reference_name=self.name,
			remarks=f"Dyeing batch {self.name}",
		)

		if out_roll:
			frappe.db.set_value(
				"Fabric Roll",
				out_roll.name,
				{
					"item_code": fg_item,
					"batch_no": batch,
					"warehouse": wh["finished"],
					"stock_entry": se,
					"stage": "Finished",
				},
				update_modified=False,
			)

		self.db_set({"stock_entry": se, "stock_posted": 1})

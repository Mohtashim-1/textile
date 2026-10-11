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


class KnittingProductionEntry(Document):
	def validate(self):
		if flt(self.yarn_issued_kg):
			self.wastage_percent = flt(self.waste_kg) / flt(self.yarn_issued_kg) * 100

	def on_submit(self):
		self.post_stock()

	def on_cancel(self):
		cancel_stock_entry(self.stock_entry)
		frappe.db.set_value(self.doctype, self.name, {"stock_entry": None, "stock_posted": 0})

	def post_stock(self):
		if self.stock_posted and self.stock_entry:
			return
		if flt(self.fabric_produced_kg) <= 0 or flt(self.yarn_issued_kg) <= 0:
			frappe.throw(_("Yarn Issued and Fabric Produced qty are required to post stock"))
		if not self.yarn_lot:
			frappe.throw(_("Yarn Lot is required to consume yarn"))

		setup_textile_stock_masters()
		wh = textile_warehouses()
		yarn = frappe.get_doc("Yarn Lot", self.yarn_lot)
		if not yarn.item_code:
			frappe.throw(_("Yarn Lot {0} has no Item. Post spinning stock first.").format(yarn.name))

		const_name = None
		if self.programme:
			construction = frappe.db.get_value("Knitting Programme", self.programme, "construction")
			if construction:
				const_name = frappe.db.get_value("Fabric Construction", construction, "construction_name")

		fab_item = ensure_item(
			item_code_for_fabric(const_name or "KNIT", "GREY"),
			item_group="Grey Fabric",
			item_name=f"Grey Knit {const_name or ''}".strip(),
		)
		roll = frappe.get_doc("Fabric Roll", self.grey_roll) if self.grey_roll else None
		batch = ensure_batch((roll.roll_no if roll else None) or f"KR-{self.name}", fab_item)

		se = manufacture_entry(
			consume=[
				{
					"item_code": yarn.item_code,
					"qty": flt(self.yarn_issued_kg),
					"warehouse": yarn.warehouse or wh["yarn"],
					"batch_no": yarn.batch_no,
				}
			],
			produce={
				"item_code": fab_item,
				"qty": flt(self.fabric_produced_kg),
				"warehouse": wh["grey"],
				"batch_no": batch,
				"rate": 240,
			},
			posting_date=self.posting_date,
			reference_doctype=self.doctype,
			reference_name=self.name,
			remarks=f"Knitting production {self.name}",
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

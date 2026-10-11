# Copyright (c) 2026, Mohtashim and contributors
# License: MIT

import frappe
from frappe.model.document import Document
from frappe.utils import flt

from textile.erpnext_stock import (
	ensure_batch,
	ensure_item,
	item_code_for_fibre,
	material_receipt,
	setup_textile_stock_masters,
	textile_warehouses,
)


class FibreLot(Document):
	def after_insert(self):
		self.post_opening_stock()

	def post_opening_stock(self):
		if self.stock_entry or flt(self.qty_kg) <= 0:
			return
		setup_textile_stock_masters()
		wh = self.warehouse or textile_warehouses()["fibre"]
		item = ensure_item(
			item_code_for_fibre(self.fibre_type or "Cotton"),
			item_group="Fibre",
			item_name=f"Fibre {self.fibre_type}",
		)
		batch = ensure_batch(self.lot_no or self.name, item)
		se = material_receipt(
			item,
			flt(self.qty_kg),
			wh,
			batch_no=batch,
			rate=120,
			posting_date=frappe.utils.today(),
			reference_doctype=self.doctype,
			reference_name=self.name,
			remarks=f"Fibre lot opening {self.lot_no}",
		)
		frappe.db.set_value(
			self.doctype,
			self.name,
			{"item_code": item, "batch_no": batch, "stock_entry": se, "warehouse": wh},
			update_modified=False,
		)
		self.item_code = item
		self.batch_no = batch
		self.stock_entry = se
		self.warehouse = wh

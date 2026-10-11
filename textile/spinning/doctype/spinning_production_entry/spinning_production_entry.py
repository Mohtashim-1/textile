# Copyright (c) 2026, Mohtashim and contributors
# License: MIT

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SpinningProductionEntry(Document):
	def validate(self):
		if flt(self.input_qty_kg):
			self.yield_percent = flt(self.output_qty_kg) / flt(self.input_qty_kg) * 100
		if self.waste_qty_kg in (None, "") and flt(self.input_qty_kg):
			self.waste_qty_kg = flt(self.input_qty_kg) - flt(self.output_qty_kg)

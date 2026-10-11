# Copyright (c) 2026, Mohtashim and contributors
# License: MIT

from frappe.model.document import Document
from frappe.utils import flt


class DyeingBatch(Document):
	def validate(self):
		self.total_cost = flt(self.dye_chemical_cost) + flt(self.utility_cost)
		if flt(self.input_qty_kg):
			self.process_loss_percent = (flt(self.input_qty_kg) - flt(self.output_qty_kg)) / flt(self.input_qty_kg) * 100
		if flt(self.output_qty_kg):
			self.cost_per_kg = flt(self.total_cost) / flt(self.output_qty_kg)

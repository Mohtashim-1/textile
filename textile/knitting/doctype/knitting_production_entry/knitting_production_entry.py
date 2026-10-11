# Copyright (c) 2026, Mohtashim and contributors
# License: MIT

from frappe.model.document import Document
from frappe.utils import flt


class KnittingProductionEntry(Document):
	def validate(self):
		if flt(self.yarn_issued_kg):
			self.wastage_percent = flt(self.waste_kg) / flt(self.yarn_issued_kg) * 100

import frappe
from textile.demo_data import ensure_roles_and_workspace


def after_install():
	ensure_roles_and_workspace()
	try:
		from textile.erpnext_stock import setup_textile_stock_masters

		setup_textile_stock_masters()
	except Exception:
		frappe.log_error(title="Textile after_install stock setup")
	frappe.clear_cache()


def after_migrate():
	ensure_roles_and_workspace()
	try:
		from textile.erpnext_stock import setup_textile_stock_masters

		setup_textile_stock_masters()
	except Exception:
		frappe.log_error(title="Textile after_migrate stock setup")

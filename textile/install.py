import frappe
from textile.demo_data import ensure_roles_and_workspace

def after_install():
	ensure_roles_and_workspace()
	frappe.clear_cache()

def after_migrate():
	ensure_roles_and_workspace()

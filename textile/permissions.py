import frappe

def check_app_permission():
	if frappe.session.user == "Administrator":
		return True
	roles = set(frappe.get_roles())
	return bool(roles.intersection({"System Manager", "Textile Manager", "Manufacturing User", "Manufacturing Manager"}))

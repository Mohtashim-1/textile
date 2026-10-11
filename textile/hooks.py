app_name = "textile"
app_title = "Textile"
app_publisher = "Mohtashim"
app_description = "Textile manufacturing vertical: Spinning, Weaving, Knitting, Dyeing & Finishing"
app_email = "shoaibmohtashim973@gmail.com"
app_license = "mit"

required_apps = ["erpnext"]

add_to_apps_screen = [
	{
		"name": "textile",
		"logo": "/assets/textile/images/textile.svg",
		"title": "Textile",
		"route": "/app/textile",
		"has_permission": "textile.permissions.check_app_permission",
	}
]

fixtures = []

after_install = "textile.install.after_install"
after_migrate = "textile.install.after_migrate"

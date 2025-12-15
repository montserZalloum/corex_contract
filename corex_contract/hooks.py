app_name = "corex_contract"
app_title = "Corex Contract"
app_publisher = "corex"
app_description = "Seconda Party Contract"
app_email = "dev@corex.com"
app_license = "mit"


on_install = "corex_contract.install_workflow.install_workflow"

# Fixtures
# --------
# Export fixtures to JSON files for version control
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			["name", "in", [
				"Contract-party_signature",
				"Contract-party_signed_on"
			]]
		]
	},
	{
		"dt": "Workflow State",
		"filters": [
			["workflow_state_name", "in", [
				"Draft",
				"Pending Party Signature",
				"Signed by Party",
				"Active"
			]]
		]
	},
	{
		"dt": "Workflow",
		"filters": [
			["workflow_name", "=", "Contract Two-Party Signature"]
		]
	},
	{
		"dt": "Web Form",
		"filters": [
			["name", "=", "sign-contract"]
		]
	},
	{
		"dt": "Notification",
		"filters": [
			["name", "in", [
				"Contract - Party Signature Required",
				"Contract - Party Signed",
				"Contract - Expiry Reminder (30 Days)",
				"Contract - Expiry Reminder (15 Days)",
				"Contract - Expiry Reminder (2 Days)"
			]]
		]
	},
	{
        "dt": "Custom DocPerm",
        "filters": [
            ["parent", "=", "Contract"],
            ["role", "=", "Customer"]
        ]
    }
]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "corex_contract",
# 		"logo": "/assets/corex_contract/logo.png",
# 		"title": "Corex Contract",
# 		"route": "/corex_contract",
# 		"has_permission": "corex_contract.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/corex_contract/css/corex_contract.css"
# app_include_js = "/assets/corex_contract/js/corex_contract.js"

# include js, css files in header of web template
# web_include_css = "/assets/corex_contract/css/corex_contract.css"
# web_include_js = "/assets/corex_contract/js/corex_contract.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "corex_contract/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Contract": "public/js/contract.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "corex_contract/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "corex_contract.utils.jinja_methods",
# 	"filters": "corex_contract.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "corex_contract.install.before_install"
# after_install = "corex_contract.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "corex_contract.uninstall.before_uninstall"
# after_uninstall = "corex_contract.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "corex_contract.utils.before_app_install"
# after_app_install = "corex_contract.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "corex_contract.utils.before_app_uninstall"
# after_app_uninstall = "corex_contract.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "corex_contract.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Contract": {
		"on_update": "corex_contract.contract_hooks.on_contract_update"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"corex_contract.tasks.all"
# 	],
# 	"daily": [
# 		"corex_contract.tasks.daily"
# 	],
# 	"hourly": [
# 		"corex_contract.tasks.hourly"
# 	],
# 	"weekly": [
# 		"corex_contract.tasks.weekly"
# 	],
# 	"monthly": [
# 		"corex_contract.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "corex_contract.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "corex_contract.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "corex_contract.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["corex_contract.utils.before_request"]
# after_request = ["corex_contract.utils.after_request"]

# Job Events
# ----------
# before_job = ["corex_contract.utils.before_job"]
# after_job = ["corex_contract.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"corex_contract.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


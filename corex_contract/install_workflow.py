import frappe

def create_custom_fields():
	"""Create custom fields for Contract"""
	fields = [
		{
			"dt": "Contract",
			"fieldname": "party_signature",
			"fieldtype": "Signature",
			"label": "Party Signature",
			"insert_after": "party_user",
			"allow_on_submit": 1,
			"no_copy": 1,
			"description": "Signature from the party (customer/supplier/employee)",
			"depends_on": "eval:doc.workflow_state=='Pending Party Signature' || doc.workflow_state=='Signed by Party' || doc.workflow_state=='Active'"
		},
		{
			"dt": "Contract",
			"fieldname": "party_signed_on",
			"fieldtype": "Datetime",
			"label": "Party Signed On",
			"insert_after": "party_signature",
			"allow_on_submit": 1,
			"read_only": 1,
			"no_copy": 1,
			"description": "Timestamp when party signed the contract",
			"depends_on": "eval:doc.party_signature"
		}
	]

	for field in fields:
		if not frappe.db.exists("Custom Field", f"{field['dt']}-{field['fieldname']}"):
			custom_field = frappe.get_doc({
				"doctype": "Custom Field",
				**field
			})
			custom_field.insert()
			print(f"Created Custom Field: {field['fieldname']}")
		else:
			print(f"Custom Field already exists: {field['fieldname']}")

def create_workflow_states():
	"""Create workflow states"""
	states = [
		{"workflow_state_name": "Draft", "style": "Primary", "icon": "file"},
		{"workflow_state_name": "Pending Party Signature", "style": "Warning", "icon": "edit"},
		{"workflow_state_name": "Signed by Party", "style": "Info", "icon": "check"},
		{"workflow_state_name": "Active", "style": "Success", "icon": "ok"}
	]

	for state in states:
		if not frappe.db.exists("Workflow State", state["workflow_state_name"]):
			workflow_state = frappe.get_doc({
				"doctype": "Workflow State",
				**state
			})
			workflow_state.insert()
			print(f"Created Workflow State: {state['workflow_state_name']}")
		else:
			print(f"Workflow State already exists: {state['workflow_state_name']}")

def create_workflow_actions():
	"""Create workflow action masters"""
	actions = [
		"Send for Signature",
		"Sign Contract",
		"Approve and Submit",
		"Reject"
	]

	for action in actions:
		if not frappe.db.exists("Workflow Action Master", action):
			workflow_action = frappe.get_doc({
				"doctype": "Workflow Action Master",
				"workflow_action_name": action
			})
			workflow_action.insert()
			print(f"Created Workflow Action: {action}")
		else:
			print(f"Workflow Action already exists: {action}")

def create_workflow():
	"""Create the main workflow"""
	workflow_name = "Contract Two-Party Signature"

	if frappe.db.exists("Workflow", workflow_name):
		print(f"Workflow already exists: {workflow_name}")
		return

	workflow = frappe.get_doc({
		"doctype": "Workflow",
		"workflow_name": workflow_name,
		"document_type": "Contract",
		"is_active": 1,
		"override_status": 0,
		"send_email_alert": 1,
		"workflow_state_field": "workflow_state",
		"states": [
			{
				"doctype": "Workflow Document State",
				"state": "Draft",
				"doc_status": "0",
				"allow_edit": "HR Manager",
				"message": "Contract is in draft state. HR can edit and send for party signature."
			},
			{
				"doctype": "Workflow Document State",
				"state": "Pending Party Signature",
				"doc_status": "0",
				"allow_edit": "Customer",
				"message": "Awaiting signature from party. Party can sign via web form."
			},
			{
				"doctype": "Workflow Document State",
				"state": "Signed by Party",
				"doc_status": "0",
				"allow_edit": "HR Manager",
				"message": "Party has signed. HR Manager can review and approve/submit."
			},
			{
				"doctype": "Workflow Document State",
				"state": "Active",
				"doc_status": "1",
				"allow_edit": "HR Manager",
				"update_field": "status",
				"update_value": "Active",
				"message": "Contract is active and submitted."
			}
		],
		"transitions": [
			{
				"doctype": "Workflow Transition",
				"state": "Draft",
				"action": "Send for Signature",
				"next_state": "Pending Party Signature",
				"allowed": "HR Manager",
				"allow_self_approval": 1,
				"condition": "doc.party_user"
			},
			{
				"doctype": "Workflow Transition",
				"state": "Pending Party Signature",
				"action": "Sign Contract",
				"next_state": "Signed by Party",
				"allowed": "Customer",
				"allow_self_approval": 1,
				"condition": "doc.party_signature"
			},
			{
				"doctype": "Workflow Transition",
				"state": "Signed by Party",
				"action": "Approve and Submit",
				"next_state": "Active",
				"allowed": "HR Manager",
				"allow_self_approval": 0,
				"condition": "doc.party_signature and doc.signee_company"
			},
			{
				"doctype": "Workflow Transition",
				"state": "Signed by Party",
				"action": "Reject",
				"next_state": "Draft",
				"allowed": "HR Manager",
				"allow_self_approval": 1
			}
		]
	})
	workflow.insert()
	print(f"Created Workflow: {workflow_name}")

def create_web_form():
	"""Create web form for party signature"""
	web_form_name = "sign-contract"

	if frappe.db.exists("Web Form", web_form_name):
		print(f"Web Form already exists: {web_form_name}")
		return

	web_form = frappe.get_doc({
		"doctype": "Web Form",
		"title": "Sign Contract",
		"route": "sign-contract",
		"doc_type": "Contract",
		"module": "CRM",
		"is_standard": 1,
		"published": 1,
		"login_required": 1,
		"allow_edit": 1,
		"allow_multiple": 0,
		"allow_delete": 0,
		"allow_print": 1,
		"allow_comments": 0,
		"show_attachments": 0,
		"allow_incomplete": 0,
		"apply_document_permissions": 1,
		"show_list": 0,
		"show_sidebar": 0,
		"button_label": "Submit Signature",
		"success_title": "Contract Signed Successfully",
		"success_message": "Thank you for signing the contract. The company will review and finalize it.",
		"introduction_text": "<h3>Contract Signature</h3><p>Please review the contract terms below and provide your signature.</p>",
		"condition_json": '[[\"Contract\",\"workflow_state\",\"=\",\"Pending Party Signature\",false]]',
		"web_form_fields": [
			{
				"fieldname": "party_name",
				"fieldtype": "Data",
				"label": "Party Name",
				"read_only": 1
			},
			{
				"fieldname": "contract_terms",
				"fieldtype": "Text Editor",
				"label": "Contract Terms",
				"read_only": 1,
				"description": "Please read the contract terms carefully before signing"
			},
			{
				"fieldname": "start_date",
				"fieldtype": "Date",
				"label": "Start Date",
				"read_only": 1
			},
			{
				"fieldname": "end_date",
				"fieldtype": "Date",
				"label": "End Date",
				"read_only": 1
			},
			{
				"fieldname": "section_break_signature",
				"fieldtype": "Section Break",
				"label": "Your Signature"
			},
			{
				"fieldname": "party_signature",
				"fieldtype": "Signature",
				"label": "Signature",
				"reqd": 1,
				"description": "Please sign in the box below"
			}
		],
		"client_script": "frappe.web_form.on('party_signature', function(field, value) {\n    if (value) {\n        frappe.web_form.set_value('party_signed_on', frappe.datetime.now_datetime());\n    }\n});"
	})
	web_form.insert()
	print(f"Created Web Form: {web_form_name}")

def create_notifications():
	"""Create email notifications"""
	notifications = [
		{
			"name": "Contract - Party Signature Required",
			"enabled": 1,
			"channel": "Email",
			"subject": "Action Required: Sign Contract {{ doc.name }}",
			"document_type": "Contract",
			"event": "Value Change",
			"value_changed": "workflow_state",
			"condition": "doc.workflow_state == 'Pending Party Signature'",
			"message": "Dear {{ doc.party_name }},\n\nPlease sign the contract by clicking: {{ frappe.utils.get_url() }}/sign-contract?name={{ doc.name }}\n\nContract Details:\n- Number: {{ doc.name }}\n- Start Date: {{ doc.start_date }}\n- End Date: {{ doc.end_date }}\n\nThank you.",
			"recipients": [
				{
					"receiver_by_document_field": "party_user"
				}
			]
		},
		{
			"name": "Contract - Party Signed",
			"enabled": 1,
			"channel": "Email",
			"subject": "Contract {{ doc.name }} - Party Signature Received",
			"document_type": "Contract",
			"event": "Value Change",
			"value_changed": "workflow_state",
			"condition": "doc.workflow_state == 'Signed by Party'",
			"message": "Contract {{ doc.name }} has been signed by {{ doc.party_name }}. Please review and approve.\n\nView contract: {{ frappe.utils.get_url() }}/app/contract/{{ doc.name }}",
			"recipients": [
				{
					"receiver_by_role": "HR Manager"
				}
			]
		}
	]

	for notif in notifications:
		if not frappe.db.exists("Notification", notif["name"]):
			notification = frappe.get_doc({
				"doctype": "Notification",
				**notif
			})
			notification.insert()
			print(f"Created Notification: {notif['name']}")
		else:
			print(f"Notification already exists: {notif['name']}")

def install_workflow():
	"""Main installation function"""
	# frappe.init(site="x.conanacademy.com")
	# frappe.connect()

	print("\n=== Installing Contract Two-Party Signature Workflow ===\n")

	print("Step 1: Creating Custom Fields...")
	create_custom_fields()

	print("\nStep 2: Creating Workflow States...")
	create_workflow_states()

	print("\nStep 3: Creating Workflow Actions...")
	create_workflow_actions()

	print("\nStep 4: Creating Workflow...")
	create_workflow()

	print("\nStep 5: Creating Web Form...")
	create_web_form()

	print("\nStep 6: Creating Notifications...")
	create_notifications()

	frappe.db.commit()
	print("\n=== Installation Complete! ===\n")

# if __name__ == "__main__":
# 	install_workflow()

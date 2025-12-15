import frappe
from frappe.utils import now_datetime

# --- THIS IS THE CORRECT, DOCUMENTED IMPORT PATH ---
from frappe.model.workflow import apply_workflow

def on_contract_update(doc, method):
	"""
	After a contract is saved, check if the party signature was just added.
	If so, set the timestamp and apply the workflow to change the state.
	"""
	# get_doc_before_save() is also available in on_update
	doc_before_save = doc.get_doc_before_save()
	if not doc_before_save:
		return

	# Proceed only if the state is 'Pending Party Signature'
	if doc.workflow_state == "Pending Party Signature":

		# Check if the signature was added in the save operation that just finished
		if doc.party_signature and not doc_before_save.party_signature:

			# 1. Set the timestamp directly in the database.
			# Use db_set in post-save hooks to avoid triggering another save cycle.
			doc.db_set('party_signed_on', now_datetime(), update_modified=False)

			# 2. Apply the workflow action. This will trigger its own save.
			apply_workflow(doc, "Sign Contract")

			send_system_notification_to_managers(doc)
			

def send_system_notification_to_managers(doc):
	"""
	Sends a clickable system notification to all enabled users with the 'System Manager' role
	by creating Notification Log documents for each of them.
	"""
	# Direct SQL query to get users with the 'System Manager' role, bypassing permissions.
	# This is necessary as the script is triggered by a 'Customer'.
	system_managers = [
		p[0] for p in frappe.db.sql("""
			SELECT `parent`
			FROM `tabHas Role`
			WHERE `role`='System Manager'
			AND `parenttype`='User'
			AND `parent` IN (SELECT `name` FROM `tabUser` WHERE `enabled`=1)
		""")
	]

	if not system_managers:
		frappe.log_error(
			title="No System Managers Found",
			message="Could not send Contract Signed notification because no enabled users with the 'System Manager' role were found."
		)
		return

	subject = f"Contract {doc.name} Signed"
	message = f"The contract <strong>{doc.name}</strong> with <i>{doc.party_name}</i> has been signed and requires review."

	# Loop through each manager and create a dedicated notification log for them.
	# This is the correct and robust method to create a system notification.
	for user in system_managers:
		notification_log = frappe.new_doc("Notification Log")
		notification_log.for_user = user
		notification_log.type = "Alert"
		notification_log.from_user = doc.modified_by or frappe.session.user
		notification_log.subject = subject
		notification_log.email_content = message  # This content is shown in the notification pop-up

		# This part makes the notification a clickable link to the contract
		notification_log.document_type = doc.doctype
		notification_log.document_name = doc.name

		# Insert the notification, ignoring permissions for the 'Customer' role.
		notification_log.insert(ignore_permissions=True)
	
	# Commit the changes to the database to ensure notifications are saved immediately.
	frappe.db.commit()
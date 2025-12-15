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

			send_signature_notification(doc)
			

def send_signature_notification(doc):
	"""
	Sends a clickable system notification to all enabled 'HR Managers' AND the document owner.
	Uses a set to prevent sending duplicate notifications.
	"""
	# 1. Get all users with the 'HR Manager' role
	hr_managers = [
		p[0] for p in frappe.db.sql("""
			SELECT `parent`
			FROM `tabHas Role`
			WHERE `role`='HR Manager'
			AND `parenttype`='User'
			AND `parent` IN (SELECT `name` FROM `tabUser` WHERE `enabled`=1)
		""")
	]

	# 2. Create a set from the list of HR Managers
	# A set is a collection of unique items.
	recipients = set(hr_managers)

	# 3. Add the document owner to the set.
	# If the owner is already in the set (i.e., they are an HR Manager),
	# the set will not change, preventing duplicate notifications.
	recipients.add(doc.owner)

	# Check if we have anyone to notify
	if not recipients:
		frappe.log_error(
			title="No Recipients for Notification",
			message=f"For Contract {doc.name}, no HR Managers were found and the owner could not be determined."
		)
		return

	subject = f"Contract {doc.name} Signed"
	message = f"The contract <strong>{doc.name}</strong> with <i>{doc.party_name}</i> has been signed and requires review."

	# 4. Loop through the final, unique list of recipients
	for user in recipients:
		notification_log = frappe.new_doc("Notification Log")
		notification_log.for_user = user
		notification_log.type = "Alert"
		notification_log.from_user = doc.modified_by or frappe.session.user
		notification_log.subject = subject
		notification_log.email_content = message
		notification_log.document_type = doc.doctype
		notification_log.document_name = doc.name
		notification_log.insert(ignore_permissions=True)
	
	frappe.db.commit()
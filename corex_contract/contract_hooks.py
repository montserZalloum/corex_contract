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


# --- REPLACE the verbose debug version with this FINAL, CLEAN version ---
from frappe.utils import nowdate, add_days, date_diff

def send_contract_expiry_reminders():
    """
    This function is run by the daily scheduler.
    It finds contracts expiring in 30, 15, or 2 days and sends
    both email and system notifications to HR Managers and the document owner.
    """
    today = nowdate()
    reminder_days = [30, 15, 2]
    target_dates = [add_days(today, days) for days in reminder_days]

    contracts_to_notify = frappe.get_all(
        "Contract",
        filters={
            "status": "Active",
            "docstatus": 1,
            "end_date": ["in", target_dates]
        },
        fields=["name", "owner", "party_name", "end_date"]
    )

    if not contracts_to_notify:
        return # Exit quietly if there are no contracts to process

    hr_managers = [
        p[0] for p in frappe.db.sql("""
            SELECT `parent` FROM `tabHas Role`
            WHERE `role`='HR Manager' AND `parenttype`='User'
            AND `parent` IN (SELECT `name` FROM `tabUser` WHERE `enabled`=1)
        """)
    ]

    for contract_data in contracts_to_notify:
        days_to_expiry = date_diff(contract_data.end_date, today)
        
        recipients = set(hr_managers)
        recipients.add(contract_data.owner)
        
        if not recipients:
            continue

        valid_recipients = [user for user in recipients if frappe.db.get_value("User", user, "enabled")]
        
        if not valid_recipients:
            continue
            
        # --- 1. Send Email ---
        email_subject = f"Contract {contract_data.name} Expires in {days_to_expiry} Days - Action Required"
        email_message = f"""
            Dear Team,<br><br>
            This is a reminder that the contract <strong>{contract_data.name}</strong> with <i>{contract_data.party_name}</i> will expire in <b>{days_to_expiry} days</b> on {contract_data.end_date}.<br><br>
            Please review this contract and take the necessary action.<br><br>
            <a href="{frappe.utils.get_url_to_form('Contract', contract_data.name)}">Click here to view the contract</a>.
        """
        frappe.sendmail(
            recipients=valid_recipients,
            subject=email_subject,
            message=email_message,
            reference_doctype="Contract",
            reference_name=contract_data.name
        )

        # --- 2. Create System Notification ---
        notification_subject = f"Contract {contract_data.name} expires in {days_to_expiry} days"
        notification_message = f"The contract with {contract_data.party_name} is expiring soon. Please review."
        
        for user in valid_recipients:
            frappe.get_doc({
                "doctype": "Notification Log",
                "for_user": user,
                "document_type": "Contract",
                "document_name": contract_data.name,
                "subject": notification_subject,
                "email_content": notification_message,
                "type": "Alert"
            }).insert(ignore_permissions=True)

    frappe.db.commit()
import frappe
from frappe.utils import now_datetime, nowdate, add_days, date_diff
from frappe.model.workflow import apply_workflow

def on_contract_update(doc, method):
	"""
	After a contract is saved, check if the party signature was just added.
	If so, set the timestamp and apply the workflow to change the state.
	"""
	doc_before_save = doc.get_doc_before_save()
	if not doc_before_save:
		return

	if doc.workflow_state == "Pending Party Signature":
		if doc.party_signature and not doc_before_save.party_signature:
			doc.db_set('party_signed_on', now_datetime(), update_modified=False)
			apply_workflow(doc, "Sign Contract")
			send_signature_notification(doc)

# --- NEW FUNCTION TO HANDLE REJECTION ---
def on_contract_rejection(doc, method):
	"""
	This function is triggered by the 'on_transition' hook.
	It checks if the workflow action was 'Reject' and clears the party's signature.
	"""
	if doc.workflow_action == "Reject":
		doc.party_signature = None
		doc.party_signed_on = None
		doc.add_comment(
			"Comment",
			text=frappe._("Contract was rejected by HR. The party's signature has been cleared and must be provided again.")
		)

def send_signature_notification(doc):
	"""
	Sends a clickable system notification to all enabled 'HR Managers' AND the document owner.
	"""
	hr_managers = [
		p[0] for p in frappe.db.sql("""
			SELECT `parent` FROM `tabHas Role`
			WHERE `role`='HR Manager' AND `parenttype`='User'
			AND `parent` IN (SELECT `name` FROM `tabUser` WHERE `enabled`=1)
		""")
	]
	recipients = set(hr_managers)
	recipients.add(doc.owner)

	if not recipients:
		# This log message is for developers/admins, so it doesn't need translation.
		frappe.log_error(
			title="No Recipients for Notification",
			message=f"For Contract {doc.name}, no HR Managers were found and the owner could not be determined."
		)
		return

	# --- Translatable Strings ---
	subject = frappe._("Contract {0} Signed").format(doc.name)
	message = frappe._("The contract <strong>{0}</strong> with <i>{1}</i> has been signed and requires review.").format(doc.name, doc.party_name)

	for user in recipients:
		frappe.get_doc({
			"doctype": "Notification Log",
			"for_user": user,
			"document_type": doc.doctype,
			"document_name": doc.name,
			"subject": subject,
			"from_user": doc.modified_by or frappe.session.user,
			"email_content": message,
			"type": "Alert"
		}).insert(ignore_permissions=True)

	frappe.db.commit()

def send_contract_expiry_reminders():
    """
    This function is run by the daily scheduler. It sends translatable
    expiry reminders for contracts.
    """
    today = nowdate()
    reminder_days = [30, 15, 2]
    target_dates = [add_days(today, days) for days in reminder_days]

    contracts_to_notify = frappe.get_all(
        "Contract",
        filters={"status": "Active", "docstatus": 1, "end_date": ["in", target_dates]},
        fields=["name", "owner", "party_name", "end_date"]
    )

    if not contracts_to_notify:
        return

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
        
        valid_recipients = [user for user in recipients if frappe.db.get_value("User", user, "enabled")]
        if not valid_recipients:
            continue
            
        # --- Prepare Translatable Content ---
        email_subject = frappe._("Contract {0} Expires in {1} Days - Action Required").format(contract_data.name, days_to_expiry)
        
        email_message = (
            frappe._("Dear Team,") + "<br><br>" +
            frappe._("This is a reminder that the contract <strong>{0}</strong> with <i>{1}</i> will expire in <b>{2} days</b> on {3}.").format(contract_data.name, contract_data.party_name, days_to_expiry, contract_data.end_date) + "<br><br>" +
            frappe._("Please review this contract and take the necessary action.") + "<br><br>" +
            '<a href="{0}">{1}</a>'.format(frappe.utils.get_url_to_form('Contract', contract_data.name), frappe._("Click here to view the contract"))
        )

        notification_subject = frappe._("Contract {0} expires in {1} days").format(contract_data.name, days_to_expiry)
        notification_message = frappe._("The contract with <i>{0}</i> is expiring soon. Please review.").format(contract_data.party_name)

        # --- Send Email and System Notifications ---
        frappe.sendmail(
            recipients=valid_recipients, subject=email_subject, message=email_message,
            reference_doctype="Contract", reference_name=contract_data.name
        )
        
        for user in valid_recipients:
            frappe.get_doc({
                "doctype": "Notification Log", "for_user": user, "document_type": "Contract",
                "document_name": contract_data.name, "subject": notification_subject,
                "email_content": notification_message, "type": "Alert"
            }).insert(ignore_permissions=True)

    frappe.db.commit()
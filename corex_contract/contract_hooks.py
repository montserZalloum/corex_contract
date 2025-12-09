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
			
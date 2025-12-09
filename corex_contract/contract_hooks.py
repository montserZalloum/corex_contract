import frappe
from frappe.utils import now_datetime

def on_contract_update(doc, method):
	"""Auto-update party_signed_on timestamp when signature is added"""
	if doc.party_signature and not doc.party_signed_on:
		doc.db_set('party_signed_on', now_datetime(), update_modified=False)

def validate_contract(doc, method):
	"""Validate and auto-transition workflow when party signs"""
	# Check if this is a signature being added via webform
	if doc.party_signature and doc.workflow_state == "Pending Party Signature":
		# Check if this is the first time the signature is being added
		if doc.has_value_changed('party_signature'):
			# Update workflow state to trigger notification
			doc.workflow_state = 'Signed by Party'

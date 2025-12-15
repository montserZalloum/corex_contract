import frappe
from frappe import _

def get_context(context):
    # Modify the attributes directly on the 'context' object
    
    # 1. Translate Introduction Text
    # We construct the HTML in Python, translating only the text parts.
    context.introduction_text = f"""
        <h3>{_("Contract Signature")}</h3>
        <p>{_("Please review the contract terms below and provide your signature.")}</p>
    """

    # 2. Translate Success Message and Title
    context.success_title = _("Contract Signed Successfully")
    context.success_message = _("Thank you for signing the contract. The company will review and finalize it.")
    
    # 3. Translate Button Label
    context.button_label = _("Submit Signature")
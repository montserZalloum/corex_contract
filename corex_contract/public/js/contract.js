frappe.ui.form.on('Contract', {
	refresh: function(frm) {
		frm.page.remove_action_item('Help');

		// Add custom button to copy signature link
		if (frm.doc.workflow_state === 'Pending Party Signature' && frm.doc.party_user) {
			frm.add_custom_button(__('Copy Signature Link'), function() {
				let url = window.location.origin + '/sign-contract/' + frm.doc.name + '/edit';
				frappe.utils.copy_to_clipboard(url);
				frappe.show_alert({
					message: __('Signature link copied to clipboard'),
					indicator: 'green'
				});
			});
		}

		// Add button to send reminder email
		// if (frm.doc.workflow_state === 'Pending Party Signature' && frm.doc.party_user) {
		// 	frm.add_custom_button(__('Send Reminder'), function() {
		// 		frappe.call({
		// 			method: 'frappe.desk.doctype.notification.notification.send_notification',
		// 			args: {
		// 				doc: frm.doc
		// 			},
		// 			callback: function(r) {
		// 				frappe.msgprint(__('Reminder sent to ') + frm.doc.party_user);
		// 			}
		// 		});
		// 	});
		// }

		
	}
});

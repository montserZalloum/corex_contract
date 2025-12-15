frappe.ready(function() {
    // Hook into the 'after_save' event
    frappe.web_form.after_save = function() {
        
        // Use setTimeout to ensure the DOM has finished updating with the "Updated" message
        setTimeout(function() {
            // 1. Define your translated strings
            var success_title = __("Contract Signed Successfully");
            var success_msg = __("Thank you for signing the contract. The company will review and finalize it.");
            var view_btn = __("View your response");

            // 2. Inject them into the existing HTML structure
            // Replace "Updated" with "Contract Signed Successfully"
            $('.success-title').text(success_title);

            // Replace "Your form has been successfully updated" with the custom message
            $('.success-message').text(success_msg);

            // Replace "View your response" (just in case)
            $('.view-button').remove();
            
        }, 100); // 100ms delay to be safe
    };
});
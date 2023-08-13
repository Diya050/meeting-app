// meeting.js

// Function to handle the "send_emails" custom button click on the Meeting doctype form
frappe.ui.form.on("Meeting", {
    send_emails: function(frm) {
        // Check if the document is new (not yet saved)
        if(frm.doc.__islocal) {
            // Display a message asking the user to save before sending emails
            msgprint(__("Please save before Sending."));
            throw "Sending error";
        } else {
            // If the document is saved and its status is "Planned," send invitation emails
            if (frm.doc.status === "Planned") {
                frappe.call({
                    method: "meeting.api.send_invitation_emails",
                    args: {
                        meeting: frm.doc.name
                    },
                    callback: function(r) {
                        frm.clear_custom_buttons(); // Clear custom buttons after sending emails
                        frm.refresh(); // Refresh the form
                    }
                });
            }
        }
    },

    // Function to handle the "send_minutes" custom button click on the Meeting doctype form
    send_minutes: function(frm) {
        // Check if the document is new (not yet saved)
        if(frm.doc.__islocal) {
            // Display a message asking the user to save before sending minutes
            msgprint(__("Please save before Sending."));
            throw "Sending error";
        } else {
            // If the document is saved and its status is "In Progress," send meeting minutes
            if (frm.doc.status === "In Progress") {
                frappe.call({
                    method: "meeting.api.send_minutes",
                    args: {
                        meeting: frm.doc.name
                    }
                });
            }
        }
    }
});

// Event handler for the Meeting Attendee doctype
frappe.ui.form.on("Meeting Attendee", {
    attendee: function(frm, cdt, cdn) {
        var attendee = frappe.model.get_doc(cdt, cdn);
        if (attendee.attendee) {
            // If attendee is selected, get the full name of the attendee
            frappe.call({
                method: "meeting.meeting.doctype.meeting.meeting.get_full_name",
                args: {
                    attendee: attendee.attendee
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "full_name", r.message); // Set the full name in the field
                }
            });
        } else {
            // If no attendee is selected, clear the full name field
            frappe.model.set_value(cdt, cdn, "full_name", null);
        }
    },
});

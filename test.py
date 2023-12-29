@frappe.whitelist()
def end_meeting_message(meeting):
    meeting = frappe.get_doc("Meeting", meeting)
    if meeting.status == "In Progress":
        message = "Meeting has ended."
        for attendee in meeting.attendees:
            frappe.publish_realtime(event="meeting_ended", message=message, user=attendee.attendee)
            
        for attendee in meeting.attendees:
            frappe.sendmail(
                recipients=[attendee.attendee],
                sender=frappe.session.user,
                subject="Meeting Ended: " + meeting.title,
                message=message
            )
        meeting.status = "Completed"
        meeting.save()
        frappe.msgprint(_("Meeting Status updated to 'Completed'"))
    else:
        frappe.msgprint(_("Meeting Status must be 'In Progress' to end the meeting"))

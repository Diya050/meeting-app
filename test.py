@frappe.whitelist()
def end_meeting_message(meeting):
    meeting = frappe.get_doc("Meeting", meeting)

    if meeting.status == "In Progress":
        try:
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

            print("Before Status Update:", meeting.status)  # Add this line

            meeting.status = "Completed"
            meeting.save()
            frappe.db.commit()
            print("Commit Successful")


            print("After Status Update:", meeting.status)  # Add this line

            frappe.msgprint(_("Meeting Status updated to 'Completed'"))
        except Exception as e:
            frappe.msgprint(_("Error updating meeting status: {0}".format(str(e))))
    else:
        frappe.msgprint(_("Meeting Status must be 'In Progress' to end the meeting"))

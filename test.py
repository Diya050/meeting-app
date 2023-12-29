@frappe.whitelist()
def send_invitation_emails(meeting):
	meeting = frappe.get_doc("Meeting", meeting)
	sender_fullname = get_fullname(frappe.session.user)

	if meeting.status == "Planned":
		if meeting.attendees:
				message = frappe.get_template("templates/emails/meeting_invitation.html").render({
					"sender":sender_fullname,
					"date":meeting.date,
					"from_time":meeting.from_time,
					"to_time":meeting.to_time,
					"invitation_message":meeting.invitation_message,
					"agenda": meeting.agenda,
					"supplementary_agenda": meeting.supplementary_agenda,
					"by_chairman_permission": meeting.by_chairman_permission,
				})
				frappe.sendmail(
				recipients=[d.attendee for d in meeting.attendees],
				sender=frappe.session.user,
				subject="New Meeting:" + meeting.title,
				message=message,
				reference_doctype=meeting.doctype,
				reference_name=meeting.name,
				)
				meeting.status = "Invitation Sent"
				meeting.save()
				frappe.msgprint(_("Invitation Sent"))
		else:
			frappe.msgprint("Enter atleast one Attendee for Sending")
	else:
		frappe.msgprint(_("Meeting Status must be 'Planned'"))

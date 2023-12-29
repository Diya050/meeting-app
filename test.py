@frappe.whitelist()
def send_minutes(meeting):
	meeting = frappe.get_doc("Meeting", meeting)
	sender_fullname = get_fullname(frappe.session.user)

	if meeting.status == "Completed":
		if meeting.minutes:
			# Prepare a message with a table containing all meeting minutes
			message = frappe.get_template("templates/emails/minute_notification.html").render({
				"sender": sender_fullname,
				"meeting_title": meeting.title,
				"minutes_list": meeting.minutes,
			})

			# Get a list of all attendees
			attendees = [attendee.attendee for attendee in meeting.attendees]

			frappe.sendmail(
				recipients=attendees,
				sender=frappe.session.user,
				subject="Meeting Minutes: " + meeting.title,
				message=message,
				reference_doctype=meeting.doctype,
				reference_name=meeting.name,
			)

			meeting.status = "Minutes Sent"
			meeting.save()
			frappe.msgprint(_("Minutes Sent"))
		else:
			frappe.msgprint("Enter at least one Minute for Sending")
	else:
		frappe.msgprint(_("Meeting Status must be 'Completed'"))

  
@frappe.whitelist()
def start_meeting_message(meeting):
    meeting = frappe.get_doc("Meeting", meeting)
    if meeting.status == "Invitation Sent":
        current_time = now_datetime()
        meeting_from_time = get_datetime(str(meeting.date) + ' ' + str(meeting.from_time))  # Convert to str
        if current_time > meeting_from_time:
            delay_seconds = (current_time - meeting_from_time).seconds
            if -120 <= delay_seconds <= 300:  # Tolerance window: -2 minutes to 5 minutes
                message = "Meeting is starting on time."
            else:
                delay_minutes = delay_seconds / 60
                message = f"The meeting is starting {delay_minutes:.1f} minutes late. Meeting has started."
        else:
            message = "Meeting has started."
        for attendee in meeting.attendees:
            frappe.publish_realtime(event="meeting_started", message=message, user=attendee.attendee)
            
        for attendee in meeting.attendees:
            frappe.sendmail(
                recipients=[attendee.attendee],
                sender=frappe.session.user,
                subject="Meeting Started: " + meeting.title,
                message=message
            )
        meeting.status = "In Progress"
        meeting.save()
        frappe.msgprint(_("Meeting Status updated to 'In Progress'"))
    else:
        frappe.msgprint(_("Meeting Status must be 'Invitation Sent' to start the meeting"))
    	
    	
@frappe.whitelist()
def get_meetings(start, end):
	if not frappe.has_permission("Meeting", "read"):
		raise frappe.PermissionError
	return frappe.db.sql("""select
		timestamp(`date`, from_time) as start,
		timestamp(`date`, to_time) as end,
		name,
		title,
		status,
		0 as all_day
	from `tabMeeting`
	where `date` between %(start)s and %(end)s""", {
		"start": start,
		"end": end
	}, as_dict=True)

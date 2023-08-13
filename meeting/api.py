# api.py

import frappe
from frappe import _
from frappe.utils import get_fullname, get_link_to_form
from frappe.utils import nowdate, add_days

# Function to send invitation emails for a meeting
@frappe.whitelist()
def send_invitation_emails(meeting):
	# Fetch the Meeting document using the provided meeting name
	meeting = frappe.get_doc("Meeting", meeting)
	
	# Get the sender's full name
	sender_fullname = get_fullname(frappe.session.user)

	if meeting.status == "Planned":
		if meeting.attendees:
			# Prepare the email content using a template and send it to all attendees
			message = frappe.get_template("templates/emails/meeting_invitation.html").render({
				"sender":sender_fullname,
				"date":meeting.date,
				"from_time":meeting.from_time,
				"to_time":meeting.to_time,
				"invitation_message":meeting.invitation_message,
				"agenda": meeting.agenda,
			})
			frappe.sendmail(
				recipients=[d.attendee for d in meeting.attendees],
				sender=frappe.session.user,
				subject="New Meeting:" + meeting.title,
				message=message,
				reference_doctype=meeting.doctype,
				reference_name=meeting.name,
			)

			# Update the meeting status to "Invitation Sent" and save the document
			meeting.status = "Invitation Sent"
			meeting.save()
			frappe.msgprint(_("Invitation Sent"))
		else:
			frappe.msgprint("Enter at least one Attendee for Sending")
	else:
		frappe.msgprint(_("Meeting Status must be 'Planned'"))

# Function to send meeting minutes
@frappe.whitelist()
def send_minutes(meeting):
	# Fetch the Meeting document using the provided meeting name
	meeting = frappe.get_doc("Meeting", meeting)
	
	# Get the sender's full name
	sender_fullname = get_fullname(frappe.session.user)
	
	if meeting.status == "Invitation Sent":
		if meeting.minutes:
			# Prepare the email content for each minute and send it to the assigned users
			for d in meeting.minutes:
				message = frappe.get_template("templates/emails/minute_notification.html").render({
					"sender":sender_fullname,
					"action": d.action,
					"description": d.description,
					"complete_by":d.complete_by
				})
				frappe.sendmail(
					recipients=d.assigned_to,
					sender=frappe.session.user,
					subject=meeting.title,
					message=message,
					reference_doctype=meeting.doctype,
					reference_name=meeting.name,
				)

			# Update the meeting status to "In Progress" and save the document
			meeting.status = "In Progress"
			meeting.save()
			frappe.msgprint(_("Minutes Sent"))
		else:
			frappe.msgprint("Enter at least one Minute for Sending")
	else:
		frappe.msgprint(_("Meeting Status must be 'Invitation Sent'"))

# Function to fetch meetings within a specified date range
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

# Function to create an orientation meeting when a new User is added
def make_orientation_meeting(doc, method):
	meeting = frappe.get_doc({
		"doctype": "Meeting",
		"title": "Orientation for {0}".format(doc.first_name),
		"date": add_days(nowdate(), 1),
		"from_time": "09:00",
		"to_time": "09:30",
		"status": "Planned",
		"attendees": [{
			"attendee": doc.name
		}]
	})
	# The System Manager might not have permission to create a Meeting, so ignore permissions
	meeting.flags.ignore_permissions = True
	meeting.insert()

	frappe.msgprint(_("Orientation meeting created"))

# Function to update minute status to "Closed" if ToDo is closed or deleted
def update_minute_status(doc, method=None):
	# Only proceed if the document is related to a Meeting and not triggered from a Meeting document
	if doc.reference_type != "Meeting" or doc.flags.from_meeting:
		return

	if method == "on_trash" or doc.status == "Closed":
		# Fetch the Meeting document related to the ToDo and update its corresponding minute status
		meeting = frappe.get_doc(doc.reference_type, doc.reference_name)
		for minute in meeting.minutes:
			if minute.todo == doc.name:
				minute.db_set("todo", None, update_modified=False)
				minute.db_set("status", "Closed", update_modified=False)

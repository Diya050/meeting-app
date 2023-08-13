# meeting.py

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator

class Meeting(WebsiteGenerator):
    # The Meeting class is a WebsiteGenerator, which means it generates website pages using a specific template.
    
    website = frappe._dict(
        template = "templates/generators/meeting.html"
    )

    def validate(self):
        # This method is called before saving the document and is used for validation purposes.
        
        # Set the page_name attribute to the lowercased name of the meeting.
        self.page_name = self.name.lower()
        
        # Call the validate_attendees method to ensure attendees have valid full names and check for duplicates.
        self.validate_attendees()

    def on_update(self):
        # This method is triggered after the document is saved.
        
        # Sync ToDos for assignments and call the send_minutes method (which seems to be commented out).
        self.sync_todos()
        #	self.send_minutes()

    def validate_attendees(self):
        """Set missing names and warn if duplicate"""
        # This method ensures that each attendee in the meeting has a valid full name set and checks for duplicate attendees.
        
        found = []
        for attendee in self.attendees:
            if not attendee.full_name:
                # If the full name is missing, fetch the full name of the attendee using the get_full_name function.
                attendee.full_name = get_full_name(attendee.attendee)

            if attendee.attendee in found:
                # If the attendee is found in the 'found' list, raise an error for duplicate attendee.
                frappe.throw(_("Attendee {0} entered twice").format(attendee.attendee))

            # Add the attendee to the 'found' list.
            found.append(attendee.attendee)

    def sync_todos(self):
        """Sync ToDos for assignments"""
        # This method synchronizes ToDos for assignments based on the minutes of the meeting.
        
        # Get the names of existing ToDos associated with this meeting.
        todos_added = [todo.name for todo in
                       frappe.get_all("ToDo",
                                      filters={
                                          "reference_type": self.doctype,
                                          "reference_name": self.name,
                                          "assigned_by": ""
                                      })
                       ]

        for minute in self.minutes:
            if minute.assigned_to and minute.status=="Open":
                # If the minute has an assigned user and is open, create a ToDo if it doesn't exist.
                if not minute.todo:
                    todo = frappe.get_doc({
                        "doctype": "ToDo",
                        "description": minute.description,
                        "reference_type": self.doctype,
                        "reference_name": self.name,
                        "owner": minute.assigned_to
                    })
                    todo.insert()

                    # Link the ToDo to the minute.
                    minute.db_set("todo", todo.name, update_modified=False)

                else:
                    # If the minute has an existing ToDo, remove it from the 'todos_added' list.
                    todos_added.remove(minute.todo)

            else:
                # If the minute is unassigned or has a status other than "Open," remove the associated ToDo.
                minute.db_set("todo", None, update_modified=False)

        for todo in todos_added:
            # Remove closed or old todos that are not associated with any minutes anymore.
            todo = frappe.get_doc("ToDo", todo)
            todo.flags.from_meeting = True
            todo.delete()

    def get_context(self, context):
        # This method is used to set the context for rendering the website page.

        # Set the 'parents' context variable to create a breadcrumb navigation link to the "Meetings" page.
        context.parents = [{"name": "meetings", "title": "Meetings"}]

@frappe.whitelist()
def get_full_name(attendee):
    # This function is a whitelisted function that retrieves the full name of a user based on the provided 'attendee' parameter.
    
    # Fetch the User document corresponding to the attendee.
    user = frappe.get_doc("User", attendee)

    # Concatenate the first name, middle name, and last name of the user (if available) and return the full name.
    return " ".join(filter(None, [user.first_name, user.middle_name, user.last_name]))


# Copyright (c) 2025, sarvadhi@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ReviewDocument(Document):
    def on_update(self):
        # Only trigger if workflow_state has changed
        if self.has_value_changed("workflow_state"):
            self.create_notification_log()
            print(f"Workflow state changed from {self.get_db_value('workflow_state')} to {self.workflow_state}")
            frappe.msgprint(f"Workflow state changed to <strong>{self.workflow_state}</strong>")

    def create_notification_log(self):
        # Build message content
        message = f"""
        <div>
            <h4>Workflow Status Updated</h4>
            <p>The status of document <strong>{self.name}</strong> has been updated to:</p>
            <p><strong style="color: green;">{self.workflow_state}</strong></p>
            <p>Updated by: {self.modified_by}</p>
            <p><a href="{self.get_url()}" target="_blank">View Document</a></p>
        </div>
        """

        users_to_notify = self.get_users_to_notify()

        # Print only if users exist
        if users_to_notify:
            print(f"Users to notify: {', '.join(users_to_notify)}")
        else:
            print("No users to notify.")

        for user in users_to_notify:
            notification = frappe.get_doc({
                "doctype": "Notification Log",
                "for_user": user,
                "subject": f"Document '{self.name}' Workflow Updated to {self.workflow_state} by {self.modified_by}",
                "message": message,
                "type": "Alert",
                "document_type": self.doctype,
                "document_name": self.name
            })
            notification.insert(ignore_permissions=True)
            print(f"Notification created for user: {user}")

        frappe.db.commit()
        if users_to_notify:
            frappe.log_error(message=f"Notification sent to {', '.join(users_to_notify)}", title="Review Document Notification")

    def get_users_to_notify(self):
        users = []

        # Add owner if exists
        if self.owner:
            users.append(self.owner)
            print(f"Owner added: {self.owner}")

        # Parse _assign field safely
        assigned_users = []
        if self._assign:
            try:
                assignees = json.loads(self._assign)  # Convert JSON string to list
                print(f"Parsed _assign field: {assignees}")
                if isinstance(assignees, list):
                    assigned_users = assignees
            except Exception as e:
                frappe.log_error(f"Error parsing _assign field: {e}", "Review Document Assign Parse Error")

        users.extend(assigned_users)

        # Get users from ToDo (fallback or additional assignment)
        todo_users = frappe.db.sql_list("""
            SELECT owner FROM `tabToDo`
            WHERE reference_type = %s AND reference_name = %s
        """, (self.doctype, self.name))
        print(f"Users from ToDo: {todo_users}")
        users.extend(todo_users)
        print(f"Users after adding ToDo: {users}")

        # Remove duplicates and filter out None values
        users = list(set(filter(None, users)))
        print(f"Users after filtering: {users}")

        print(f"Final users to notify: {', '.join(users)}")
        return users
# Copyright (c) 2025, sarvadhi@gmail.com
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ReviewDocument(Document):
    def on_update(self):
        try:
            if self.has_value_changed("workflow_state"):
                self.create_notification_log()
                frappe.msgprint(f"Workflow state changed to <strong>{self.workflow_state}</strong>")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error in on_update")

    def create_notification_log(self):
        try:
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
            if not users_to_notify:
                frappe.logger().info(f"No users to notify for document {self.name}")
                return

            for user in users_to_notify:
                try:
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
                except Exception as notify_err:
                    frappe.log_error(frappe.get_traceback(), f"Notification creation failed for user {user}")

            frappe.db.commit()
            frappe.log_error(
                message=f"Notification sent to {', '.join(users_to_notify)}",
                title="Review Document Notification"
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error in create_notification_log")

    def get_users_to_notify(self):
        users = set()

        if self.owner:
            users.add(self.owner)

        if self._assign:
            try:
                assignees = json.loads(self._assign)
                if isinstance(assignees, list):
                    users.update(assignees)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Error parsing _assign field")

        try:
            todo_users = frappe.db.get_all(
                "ToDo",
                filters={"reference_type": self.doctype, "reference_name": self.name},
                fields=["owner"]
            )
            users.update(todo["owner"] for todo in todo_users if todo.get("owner"))
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error fetching ToDo users")

        return list(users)

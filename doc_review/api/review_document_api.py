
import frappe
from datetime import timedelta
from frappe.utils import now_datetime
@frappe.whitelist(allow_guest=True)
def mark_stale_documents(doc=None,method=None):
    """
    This function is called daily by the scheduler.
    It finds documents in 'In Review' state that haven't been updated in 7 days,
    and marks them as 'Stale', then adds a comment.
    """
    seven_days_ago = now_datetime() - timedelta(days=7)
    # seven_days_ago=now_datetime()-timedelta(hours=1)
    print(f"Checking for documents in 'In Review' older than {seven_days_ago}")

    # Get all documents in "In Review" that were modified before 7 days ago
    docs = frappe.get_all(
        "Review Document",
        filters={
            "workflow_state": "",
            "modified": ("<", seven_days_ago.strftime("%Y-%m-%d %H:%M:%S"))
        },
        pluck="name"
    )
    print(f"Documents to mark as stale: {docs}")
    for doc_name in docs:
        doc = frappe.get_doc("Review Document", doc_name)
        print(f"Processing document: {doc_name}")

        # Set new workflow state
        doc.db_set("workflow_state", "Stale", update_modified=False)
        print(f"Document {doc_name} marked as Stale")

        # Add a comment
        doc.add_comment(
            comment_type="Info",
            text="⚠️ Marked as stale due to inactivity (more than 7 days in In Review)."
        )
        print(f"Comment added to document {doc_name}")
        frappe.db.commit()
        frappe.logger().info(f"Document {doc_name} marked as Stale due to inactivity.")
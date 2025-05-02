
import frappe
from datetime import timedelta
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True)
def mark_stale_documents(doc=None, method=None):
    """
    Scheduled function to mark 'Review Document' entries as 'Stale'
    if they have been in 'In Review' state without modification for more than 7 days.
    """

    try:
        # cutoff_time = now_datetime() - timedelta(days=7)
        cutoff_time = now_datetime() - timedelta(seconds=15)  
        stale_docs = frappe.get_all(
            "Review Document",
            filters={
                "workflow_state": "In Review",
                "modified": ("<", cutoff_time.strftime("%Y-%m-%d %H:%M:%S"))
            },
            pluck="name"
        )

        if not stale_docs:
            frappe.logger().info("No stale documents found to update.")
            return {"message":"No stale documents found to update."}

        for doc_name in stale_docs:
            try:
                doc = frappe.get_doc("Review Document", doc_name)
                doc.db_set("workflow_state", "Stale", update_modified=False)

                doc.add_comment(
                    comment_type="Info",
                    text="⚠️ Marked as stale due to inactivity (more than 7 days in 'In Review')."
                )

                frappe.db.commit()
                frappe.logger().info(f"Marked document '{doc_name}' as Stale.")

            except Exception as doc_err:
                frappe.log_error(
                    title=f"Failed to mark '{doc_name}' as stale",
                    message=frappe.get_traceback()
                )
        return {"meassage":"Status Successfully updated to Stale"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in mark_stale_documents scheduler task")
        return {"meassage":"Status"}


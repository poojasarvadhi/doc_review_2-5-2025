# Copyright (c) 2025, sarvadhi@gmail.com and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    return [
        {"label": _("Title"), "fieldname": "title", "fieldtype": "Data", "width": 200},
        {"label": _("Category"), "fieldname": "category", "fieldtype": "Select", "options": "Policy\nProcess\nProposal\nOther", "width": 100},
        {"label": _("Workflow State"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 120},
        {"label": _("Owner"), "fieldname": "owner", "fieldtype": "Data", "width": 120},
    ]

def get_data():
    return frappe.db.get_all(
        "Review Document",
        fields=["title", "category", "workflow_state", "owner"],
        order_by="modified desc"
    )

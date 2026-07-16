import frappe
from frappe.database.sequence import create_sequence

def execute():
    # Force creation of sequences for autoincrement doctypes to fix 'Unknown SEQUENCE' error
    doctypes = [
        "Patient Name",
        "Procedure",
        "Post Mortem Report",
        "Pet History",
        "Pet Order"
    ]
    
    for dt in doctypes:
        try:
            if frappe.db.exists("DocType", dt):
                create_sequence(dt, check_not_exists=True)
        except Exception:
            pass
    
    frappe.db.commit()

import frappe
from frappe.model.naming import getseries

def execute():
    doctypes_to_migrate = [
        'Vaccinations',
        'Student Fees',
        'Vaccination Detail',
        'Drug Detail',
        'Procedure Pet',
        'Prescription Item'
    ]

    for doctype in doctypes_to_migrate:
        # Check if doctype exists
        if not frappe.db.exists('DocType', doctype):
            continue

        records = frappe.get_all(doctype, fields=['name'])
        for record in records:
            old_name = record.name
            if len(old_name) == 10 and old_name.isdigit():
                continue
            
            new_name = getseries('VETSEQ', 10)
            try:
                frappe.rename_doc(doctype, old_name, new_name, ignore_if_exists=True)
            except Exception:
                pass

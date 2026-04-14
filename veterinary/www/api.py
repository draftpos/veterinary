import frappe
from frappe.utils import nowdate
from frappe.model.document import Document

def sync_pet_history(doc, method):
    if not doc.custom_pet_details:
        return

    for row in doc.custom_pet_details:

        # unique key per pet per quotation
        filters = {
            "quotation": doc.name,
            "patient_name": row.patient_name
        }

        history_name = frappe.db.exists("Pet History", filters)

        if history_name:
            history = frappe.get_doc("Pet History", history_name)
        else:
            history = frappe.new_doc("Pet History")
            history.quotation = doc.name
            history.patient_name = row.patient_name

        # ---- PET DETAILS ----
        history.patient_owner = row.patient_owner
        history.visit_date = nowdate()

        # ---- METRICS ----
        history.weight = row.weight
        history.hr = row.hr
        history.rr = row.rr
        history.hyd = row.hyd
        history.crt = row.crt

        # ---- CONCLUSIONS ----
        history.complaint = row.complaint
        history.diagnosis = row.diagnosis
        history.differential_diagnosis = row.differential_diagnosis
        history.advices = row.advices

        history.save(ignore_permissions=True)



def before_save(doc, method):
    if doc.custom_pet_details:
        for row in doc.custom_pet_details:
            row.follow_up_date = doc.custom_follow_up_date

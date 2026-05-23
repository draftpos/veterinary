# Copyright (c) 2026, Veterinary Contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def before_save(doc, method):
    # Auto-fix schema once if needed
    fix_database_schema()

    pet_details = getattr(doc, "custom_pet_details", None)
    if pet_details:
        follow_up = getattr(doc, "custom_follow_up_date", None) or getattr(doc, "custom_inline_next_follow_up_date", None)
        if follow_up:
            for row in pet_details:
                row.follow_up_date = follow_up

    sync_veterinary_records(doc, method)


def sync_veterinary_records(doc, method):
    """
    Sync logic to propagate data from Quotation to Pet Order, Pet History, and Admissions.
    """
    custom_patient_name = getattr(doc, "custom_patient_name", None)
    custom_is_group = getattr(doc, "custom_is_group", None)
    custom_pet_details = getattr(doc, "custom_pet_details", None)

    if not custom_patient_name and not (custom_is_group and custom_pet_details):
        return

    # Collect pets to process
    pets_to_sync = []
    if custom_is_group and custom_pet_details:
        for row in custom_pet_details:
            pets_to_sync.append({
                "patient_name": row.patient_name,
                "patient_owner": row.patient_owner,
                "diagnosis": row.diagnosis,
                "complaint": row.complaint,
                "advices": row.advices,
                "hyd": row.hyd,
                "crt": row.crt,
                "weight": row.weight,
                "rr": row.rr,
                "hr": row.hr,
                "differential_diagnosis": row.differential_diagnosis,
                "is_admited": row.is_admited,
                "vaccinations": row.vaccinations,
                "prescriptions": row.prescriptions
            })
    else:
        pets_to_sync.append({
            "patient_name": doc.custom_patient_name,
            "patient_owner": getattr(doc, "custom_patient_owner", None),
            "diagnosis": getattr(doc, "custom_diagnosis", None),
            "complaint": getattr(doc, "custom_complaint", None),
            "advices": getattr(doc, "custom_advices", None),
            "hyd": getattr(doc, "custom_hyd", None),
            "crt": getattr(doc, "custom_crt", None),
            "weight": getattr(doc, "custom_weight", None),
            "rr": getattr(doc, "custom_rr", None),
            "hr": getattr(doc, "custom_hr", None),
            "differential_diagnosis": getattr(doc, "custom_differential_diagnosis", None),
            "is_admited": getattr(doc, "custom_is_admited", None),
            "vaccinations": getattr(doc, "custom_vaccinations", None),
            "prescriptions": getattr(doc, "custom_prescriptions", None)
        })

    for pet in pets_to_sync:
        if not pet["patient_name"]:
            continue

        # ---- 1. Sync Pet History ----
        history_name = frappe.db.get_value("Pet History", {"patient_name": pet["patient_name"]}, "name")
        if history_name:
            history = frappe.get_doc("Pet History", history_name)
        else:
            history = frappe.new_doc("Pet History")
            history.patient_name = pet["patient_name"]

        history.patient_owner = pet["patient_owner"]
        history.diagnosis = pet["diagnosis"]
        history.complaint = pet["complaint"]
        history.advices = pet["advices"]
        history.hyd = pet["hyd"]
        history.crt = pet["crt"]
        history.weight = pet["weight"]
        history.rr = pet["rr"]
        history.hr = pet["hr"]
        history.differential_diagnosis = pet["differential_diagnosis"]
        
        if history_name:
            history.save(ignore_permissions=True)
        else:
            history.insert(ignore_permissions=True)

        # ---- 2. Sync Pet Order (Medical Exam/Prescription) ----
        order_name = frappe.db.get_value("Pet Order", {"quotation": doc.name, "patient_name": pet["patient_name"]}, "name")
        if order_name:
            order = frappe.get_doc("Pet Order", order_name)
        else:
            order = frappe.new_doc("Pet Order")
            order.quotation = doc.name
            order.patient_name = pet["patient_name"]

        order.patient_owner = pet["patient_owner"]
        order.complaint = pet["complaint"]
        order.diagnosis = pet["diagnosis"]
        order.advices = pet["advices"]
        order.hyd = pet["hyd"]
        order.crt = pet["crt"]
        order.weight = pet["weight"]
        order.rr = pet["rr"]
        order.hr = pet["hr"]
        
        # Sync prescriptions
        order.set("prescriptions", [])
        if pet["prescriptions"]:
            for p in pet["prescriptions"]:
                order.append("prescriptions", {
                    "item_name": p.item_name,
                    "quantity": p.quantity,
                    "dosage": p.dosage,
                    "amount": p.amount
                })
        
        if order_name:
            order.save(ignore_permissions=True)
        else:
            order.insert(ignore_permissions=True)

        # ---- 3. Sync Admissions ----
        if pet["is_admited"]:
            adm_name = frappe.db.get_value("Admissions", {"quotation": doc.name, "patient_name": pet["patient_name"]}, "name")
            if adm_name:
                adm = frappe.get_doc("Admissions", adm_name)
            else:
                adm = frappe.new_doc("Admissions")
                adm.quotation = doc.name
                adm.patient_name = pet["patient_name"]

            adm.patient_owner = pet["patient_owner"]
            if adm_name:
                adm.save(ignore_permissions=True)
            else:
                adm.insert(ignore_permissions=True)


def fix_database_schema():
    """Fix Pet History columns that were accidentally restricted and clear cache."""
    try:
        # Check if Pet History columns are set correctly
        columns = ["diagnosis", "complaint", "advices", "differential_diagnosis"]
        for col in columns:
            frappe.db.sql(f"ALTER TABLE `tabPet History` MODIFY COLUMN `{col}` TEXT")
        
        frappe.clear_cache()
    except Exception:
        pass

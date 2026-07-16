# Copyright (c) 2026, Veterinary Contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.naming import getseries

def global_autoname(doc, method):
    hash_doctypes = [
        'Vaccinations', 'Student Fees', 'Vaccination Detail', 
        'Drug Detail', 'Procedure Pet', 'Prescription Item'
    ]
    if doc.doctype in hash_doctypes:
        # Generate 4 digit sequential IDs for these doctypes instead of hashes
        if not doc.name:
            prefix = f"{doc.doctype}-seq-"
            doc.name = getseries(prefix, 4).replace(prefix, "")

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

@frappe.whitelist(allow_guest=True)
def on_update(doc, method):
    sync_veterinary_records(doc, method)


def sync_veterinary_records(doc, method):
    """
    Sync logic to propagate data from Quotation to Pet Order, Pet History, and Admissions.
    """
    custom_patient_name = getattr(doc, "custom_patient_name", None)
    custom_is_group = getattr(doc, "custom_is_group", None)
    custom_pet_details = getattr(doc, "custom_pet_details", None)

    if not custom_patient_name and not (custom_is_group and custom_pet_details):
        pass # Allow it to continue to process Procedures or Vaccinations even if Patient Name is empty

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
            "vaccinations": getattr(doc, "custom_vaccination_details", None),
            "prescriptions": getattr(doc, "custom_prescriptions", None)
        })

    for pet in pets_to_sync:
        if pet.get("patient_name"):
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
                    item_code = getattr(p, "item_code", getattr(p, "item_name", getattr(p, "drug_item", None)))
                    item_info = frappe.db.get_value("Item", item_code, ["item_name", "stock_uom"], as_dict=True) if item_code else {}
                    
                    order.append("prescriptions", {
                        "item_code": item_code,
                        "item_name": item_info.get("item_name") or item_code,
                        "uom": getattr(p, "uom", None) or item_info.get("stock_uom") or "Nos",
                        "stock_uom": getattr(p, "uom", None) or item_info.get("stock_uom") or "Nos",
                        "quantity": p.quantity,
                        "qty": getattr(p, "qty", p.quantity),
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

        # ---- 4. Sync Vaccinations ----
        if pet.get("vaccinations"):
            vacc_name = frappe.db.get_value("Vaccinations", {"quotation": doc.name, "patient_name": pet["patient_name"]}, "name")
            if vacc_name:
                vacc = frappe.get_doc("Vaccinations", vacc_name)
            else:
                vacc = frappe.new_doc("Vaccinations")
                vacc.quotation = doc.name
                vacc.patient_name = pet["patient_name"]

            vacc.set("vaccination_details", [])
            for v in pet["vaccinations"]:
                vacc.append("vaccination_details", {
                    "vaccine": getattr(v, "vaccine", None),
                    "batch": getattr(v, "batch", None),
                    "date": getattr(v, "date", None),
                    "user": getattr(v, "user", None),
                    "next_follow_up_date": getattr(v, "next_follow_up_date", None),
                    "status": getattr(v, "status", None)
                })
            
            vacc.flags.ignore_sync_quotation = True
            if vacc_name:
                vacc.save(ignore_permissions=True)
            else:
                vacc.insert(ignore_permissions=True)

    # ---- 5. Sync Procedure ----
    has_procedure = getattr(doc, "custom_procedure_doctor_name", None) or getattr(doc, "custom_procedure_start_time", None) or getattr(doc, "custom_procedure_types", None)
    if has_procedure:
        proc_name = frappe.db.get_value("Procedure", {"quotation": doc.name}, "name")
        if proc_name:
            proc = frappe.get_doc("Procedure", proc_name)
        else:
            proc = frappe.new_doc("Procedure")
            proc.quotation = doc.name

        proc.is_group = doc.custom_is_group
        if not proc.is_group:
            proc.patient_name = getattr(doc, "custom_patient_name", None)
            proc.patient_owner = getattr(doc, "custom_patient_owner", None)
        else:
            proc.patient_name = None
            proc.patient_owner = None

        proc.doctor_name = getattr(doc, "custom_procedure_doctor_name", None)
        proc.start_time = getattr(doc, "custom_procedure_start_time", None)
        proc.end_time = getattr(doc, "custom_procedure_end_time", None)
        proc.medical_examination = getattr(doc, "custom_procedure_medical_examination", None)
        proc.order_id = getattr(doc, "custom_procedure_order_id", None)
        proc.reference_number = getattr(doc, "custom_procedure_reference_number", None)

        proc.set("prescriptions", [])
        if getattr(doc, "custom_procedure_prescriptions", None):
            for p in doc.custom_procedure_prescriptions:
                proc.append("prescriptions", {
                    "drug_item": getattr(p, "drug_item", getattr(p, "item_code", getattr(p, "item_name", None))),
                    "dosage": getattr(p, "dosage", None),
                    "quantity": getattr(p, "quantity", None),
                    "instructions": getattr(p, "instructions", None)
                })

        proc.set("procedure_types", [])
        if getattr(doc, "custom_procedure_types", None):
            for pt in doc.custom_procedure_types:
                proc.append("procedure_types", {
                    "patient_name": getattr(pt, "patient_name", None),
                    "procedure_type": getattr(pt, "procedure_type", None)
                })
        
        proc.flags.ignore_sync_quotation = True
        if proc_name:
            proc.save(ignore_permissions=True)
        else:
            proc.insert(ignore_permissions=True)



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

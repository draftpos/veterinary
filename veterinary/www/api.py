import frappe
from frappe.utils import nowdate
from frappe.model.document import Document


def _get_items_as_prescriptions(doc):
    """Extract prescription items from Quotation items for single-pet quotes."""
    prescriptions = []
    for item in doc.items:
        prescriptions.append(frappe._dict({
            "item_name": item.item_code,
            "quantity": item.qty,
            "amount": item.amount,
            "dosage": item.custom_dosage or ""
        }))
    return prescriptions


def sync_veterinary_records(doc, method):
    # Collect all pets to sync
    pets_to_sync = []

    if doc.custom_is_group and doc.custom_pet_details:
        for row in doc.custom_pet_details:
            pets_to_sync.append({
                "patient_name": row.patient_name,
                "patient_owner": row.patient_owner,
                "weight": row.weight,
                "hyd": row.hyd,
                "crt": row.crt,
                "hr": row.hr,
                "rr": row.rr,
                "diagnosis": row.diagnosis,
                "complaint": row.complaint,
                "advices": row.advices,
                "differential_diagnosis": row.differential_diagnosis,
                "is_admited": getattr(row, 'is_admited', False),
                "adm_doctor": getattr(row, 'adm_doctor', None),
                "prescriptions": getattr(row, 'prescriptions', [])
            })
    else:
        # Single pet from parent fields
        pets_to_sync.append({
            "patient_name": doc.custom_inline_patient_name,
            "patient_owner": doc.custom_inline_patient_owner,
            "weight": doc.custom_inline_weight,
            "hyd": doc.custom_inline_hyd,
            "crt": doc.custom_inline_crt,
            "hr": doc.custom_inline_hr,
            "rr": doc.custom_inline_rr,
            "diagnosis": doc.custom_inline_diagnosis,
            "complaint": doc.custom_inline_complaint,
            "advices": doc.custom_inline_advices,
            "differential_diagnosis": doc.custom_inline_diff_diagnosis,
            "is_admited": doc.custom_is_admitted,
            "adm_doctor": doc.custom_inline_adm_doctor,
            "adm_bed": doc.custom_inline_adm_bed,
            "adm_checkin": doc.custom_inline_adm_checkin,
            "adm_checkout": doc.custom_inline_adm_checkout,
            "prescriptions": _get_items_as_prescriptions(doc)
        })

    for pet in pets_to_sync:
        if not pet["patient_name"]:
            continue

        # Unique filters per pet per quotation
        filters = {
            "quotation": doc.name,
            "patient_name": pet["patient_name"]
        }

        # ---- 1. Sync Pet History ----
        history_name = frappe.db.exists("Pet History", filters)
        if history_name:
            history = frappe.get_doc("Pet History", history_name)
        else:
            history = frappe.new_doc("Pet History")
            history.quotation = doc.name
            history.patient_name = pet["patient_name"]

        history.patient_owner = pet["patient_owner"]
        history.visit_date = nowdate()
        history.weight = pet["weight"]
        history.hr = pet["hr"]
        history.rr = pet["rr"]
        history.hyd = pet["hyd"]
        history.crt = pet["crt"]
        history.complaint = pet["complaint"]
        history.diagnosis = pet["diagnosis"]
        history.differential_diagnosis = pet["differential_diagnosis"]
        history.advices = pet["advices"]
        history.save(ignore_permissions=True)

        # ---- 2. Sync Pet Order (Medical Examination + Prescriptions) ----
        if pet["diagnosis"] or pet["prescriptions"] or pet["complaint"]:
            order_name = frappe.db.exists("Pet Order", filters)
            if order_name:
                order = frappe.get_doc("Pet Order", order_name)
            else:
                order = frappe.new_doc("Pet Order")
                order.quotation = doc.name
                order.patient_name = pet["patient_name"]

            order.patient_owner = pet["patient_owner"]
            order.is_admited = pet["is_admited"]
            order.weight = pet["weight"]
            order.hyd = pet["hyd"]
            order.crt = pet["crt"]
            order.hr = pet["hr"]
            order.rr = pet["rr"]
            order.diagnosis = pet["diagnosis"]
            order.complaint = pet["complaint"]
            order.advices = pet["advices"]
            order.differential_diagnosis = pet["differential_diagnosis"]

            if pet["prescriptions"]:
                order.set("prescriptions", [])
                for p in pet["prescriptions"]:
                    order.append("prescriptions", {
                        "item_name": p.item_name,
                        "quantity": p.quantity,
                        "amount": p.amount,
                        "dosage": p.dosage
                    })

            order.save(ignore_permissions=True)

        # ---- 3. Sync Admissions ----
        if pet["is_admited"]:
            adm_name = frappe.db.get_value("Admissions", filters, "name")
            if adm_name:
                adm = frappe.get_doc("Admissions", adm_name)
            else:
                adm = frappe.new_doc("Admissions")
                adm.quotation = doc.name
                adm.patient_name = pet["patient_name"]

            adm.doctorname = pet.get("adm_doctor")
            adm.bed_no = pet.get("adm_bed")
            adm.checkin_time = pet.get("adm_checkin") or frappe.utils.now_datetime()
            adm.checkout_time = pet.get("adm_checkout") or None

            if adm_name:
                adm.save(ignore_permissions=True)
            else:
                adm.insert(ignore_permissions=True)


def fix_database_schema():
    """Fix Pet History columns that were accidentally restricted and clear cache."""
    # Force Frappe to forget the broken autoincrement setting
    try:
        frappe.clear_cache(doctype="Admissions")
    except Exception:
        pass

    # Numeric metrics
    for field in ['weight', 'hr', 'rr', 'crt']:
        try:
            frappe.db.sql(f"ALTER TABLE `tabPet History` MODIFY COLUMN `{field}` DECIMAL(21, 9)")
        except Exception:
            pass

    # String/Dropdown fields
    for field in ['hyd']:
        try:
            frappe.db.sql(f"ALTER TABLE `tabPet History` MODIFY COLUMN `{field}` VARCHAR(255)")
        except Exception:
            pass


def before_save(doc, method):
    # Auto-fix schema once if needed
    fix_database_schema()

    if doc.custom_pet_details:
        for row in doc.custom_pet_details:
            row.follow_up_date = doc.custom_follow_up_date

    sync_veterinary_records(doc, method)

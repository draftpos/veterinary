import frappe

def before_request():
    if not frappe.cache().get_value("pet_details_schema_synced"):
        try:
            frappe.db.updatedb("Pet Details")
            frappe.db.updatedb("Procedure")
            frappe.cache().set_value("pet_details_schema_synced", 1)
        except Exception:
            pass

@frappe.whitelist(allow_guest=True)
def sync_db():
    try:
        frappe.db.updatedb("Pet Details")
        frappe.db.updatedb("Procedure")
        frappe.db.commit()
        return "Database synced successfully for Pet Details and Procedure."
    except Exception as e:
        return f"Error: {str(e)}"

@frappe.whitelist()
def get_quotation_medical_records(quotation):
    q_doc = frappe.get_doc("Quotation", quotation)
    
    # FORCE hide standalone payment status fields in the database
    try:
        frappe.db.set_value("Custom Field", "Quotation-custom_procedure_payment_status", "hidden", 1)
        frappe.db.set_value("Custom Field", "Quotation-custom_vaccination_payment_status", "hidden", 1)
        frappe.db.commit()
    except Exception:
        pass
    
    # Collect all patients associated with this quotation
    patients = set()
    if q_doc.custom_patient_name:
        patients.add(q_doc.custom_patient_name)
    
    if hasattr(q_doc, "custom_pet_details"):
        for row in q_doc.custom_pet_details:
            if row.patient_name:
                patients.add(row.patient_name)

    # Helper to fetch and process records
    def fetch_records(doctype, item_doctype, item_fields):
        all_records = []
        
        # 1. Get records already linked to this quotation
        linked = frappe.get_all(doctype, filters={"quotation": quotation}, 
            fields=["*"], ignore_permissions=True)
        all_records.extend(linked)
        
        linked_names = [r.name for r in linked]
        
        # 2. Get records for ALL patients that have NO quotation linked
        for patient in patients:
            unlinked = frappe.get_all(doctype, filters={
                "patient_name": patient,
                "quotation": ["in", ["", None]]
            }, fields=["*"], ignore_permissions=True)
            
            for r in unlinked:
                if r.name not in linked_names:
                    frappe.db.set_value(doctype, r.name, "quotation", quotation)
                    all_records.append(r)
                    linked_names.append(r.name)
        
        frappe.db.commit()

        # 3. Fetch child items and pet details for all collected records
        for r in all_records:
            r.items = frappe.get_all(item_doctype, filters={"parent": r.name}, fields=item_fields)
            p_pets = frappe.get_all("Patient Name", filters={"name": r.patient_name}, 
                fields=["patient_name", "species", "breed", "sex", "dob"]) if r.patient_name else []
            r.pet = p_pets[0] if p_pets else {}
        
        return all_records

    procs = fetch_records("Procedure", "Drug Detail", ["drug_item", "quantity", "dosage", "instructions"])
    vacs = fetch_records("Vaccinations", "Vaccination Detail", ["vaccine", "batch", "date", "status", "next_follow_up_date", "user"])

    # System-wide debug check
    all_procs = frappe.get_all("Procedure", limit=5, fields=["name", "patient_name", "quotation"])
    all_vacs = frappe.get_all("Vaccinations", limit=5, fields=["name", "patient_name", "quotation"])

    return {
        "procedures": procs,
        "vaccinations": vacs,
        "debug_all": {
            "all_procs_sample": all_procs,
            "all_vacs_sample": all_vacs,
            "patient_used_for_search": list(patients)
        }
    }

@frappe.whitelist()
def fix_unlinked_records():
    """
    Finds Procedures and Vaccinations with empty quotation fields and 
    attempts to link them to the most recent Quotation for the same patient.
    """
    for doctype in ["Procedure", "Vaccinations"]:
        records = frappe.get_all(doctype, filters={"quotation": ["in", ["", None]]}, fields=["name", "patient_name"])
        for r in records:
            if not r.patient_name:
                continue
            
            # Find the most recent Quotation for this patient
            quotation = frappe.get_all("Quotation", 
                filters={
                    "custom_patient_name": r.patient_name, 
                    "docstatus": ["!=", 2]
                },
                order_by="creation desc",
                limit=1)
            
            if quotation:
                frappe.db.set_value(doctype, r.name, "quotation", quotation[0].name)
                frappe.db.commit()
    
    return "Fix completed."

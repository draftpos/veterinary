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
    procs = frappe.get_all("Procedure", filters={"quotation": quotation}, 
        fields=["name", "patient_name", "patient_owner", "custom_payment_status", "creation", "doctor_name", "start_time", "end_time", "medical_examination"])
    
    for p in procs:
        p.items = frappe.get_all("Drug Detail", filters={"parent": p.name}, 
            fields=["drug_item", "quantity", "dosage", "instructions"])
        p.pet = frappe.get_all("Patient Name", filters={"name": p.patient_name}, 
            fields=["patient_name", "species", "breed", "sex", "dob"])[0] if p.patient_name else {}

    vacs = frappe.get_all("Vaccinations", filters={"quotation": quotation}, 
        fields=["name", "patient_name", "custom_payment_status", "creation"])
    
    for v in vacs:
        v.items = frappe.get_all("Vaccination Detail", filters={"parent": v.name}, 
            fields=["vaccine", "batch", "date", "status", "next_follow_up_date", "user"])
        v.pet = frappe.get_all("Patient Name", filters={"name": v.patient_name}, 
            fields=["patient_name", "species", "breed", "sex", "dob"])[0] if v.patient_name else {}

    return {
        "procedures": procs,
        "vaccinations": vacs
    }

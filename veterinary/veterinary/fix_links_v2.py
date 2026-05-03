import frappe
from frappe.utils import get_datetime

def execute():
    print("=== FIXING LINKS V2: Time-based linking ===")
    
    # 1. Unlink everything linked by the previous script (optional but safer)
    # Actually, let's just find all Procedures/Vaccinations and re-evaluate their links if they are currently linked.
    
    doctypes = ["Procedure", "Vaccinations"]
    
    for dt in doctypes:
        print(f"\nProcessing {dt}...")
        records = frappe.get_all(dt, fields=["name", "creation", "patient_name", "quotation"])
        
        for r in records:
            if not r.patient_name:
                continue
                
            # If already linked, check if it makes sense
            if r.quotation:
                q_creation = frappe.db.get_value("Quotation", r.quotation, "creation")
                if q_creation:
                    diff = abs((get_datetime(r.creation) - get_datetime(q_creation)).total_seconds())
                    if diff > 3600 * 24: # More than 24 hours apart
                        print(f"  Unlinking {dt} {r.name} from {r.quotation} (Time diff: {diff/3600:.1f} hours)")
                        frappe.db.set_value(dt, r.name, "quotation", None)
                        r.quotation = None
            
            # If orphaned, try to link to a quotation created within 24 hours
            if not r.quotation:
                # Find quotations for this patient
                quotations = frappe.get_all("Quotation", 
                    filters={"custom_patient_name": r.patient_name}, 
                    fields=["name", "creation"],
                    order_by="creation desc"
                )
                
                for q in quotations:
                    diff = abs((get_datetime(r.creation) - get_datetime(q.creation)).total_seconds())
                    if diff < 3600 * 24: # Within 24 hours
                        print(f"  Linking {dt} {r.name} -> {q.name} (Time diff: {diff/3600:.1f} hours)")
                        frappe.db.set_value(dt, r.name, "quotation", q.name)
                        break

    frappe.db.commit()
    print("\nDone.")

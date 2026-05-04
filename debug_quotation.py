import frappe
from veterinary.veterinary.utils import get_quotation_medical_records

def debug_quotation(q_name):
    print(f"Debugging Quotation: {q_name}")
    data = get_quotation_medical_records(q_name)
    print(f"Procedures: {len(data['procedures'])}")
    print(f"Vaccinations: {len(data['vaccinations'])}")
    
    # Try searching by patient if empty
    if not data['procedures'] and not data['vaccinations']:
        q = frappe.get_doc("Quotation", q_name)
        patient = q.custom_patient_name
        print(f"Patient for Quotation: {patient}")
        if patient:
            p_procs = frappe.get_all("Procedure", filters={"patient_name": patient})
            p_vacs = frappe.get_all("Vaccinations", filters={"patient_name": patient})
            print(f"Total Procedures for Patient: {len(p_procs)}")
            print(f"Total Vaccinations for Patient: {len(p_vacs)}")
            for p in p_procs:
                p_doc = frappe.get_doc("Procedure", p.name)
                print(f"Procedure {p.name} quotation: '{p_doc.quotation}'")

if __name__ == "__main__":
    # Get any quotation name
    q = frappe.get_all("Quotation", limit=1)
    if q:
        debug_quotation(q[0].name)
    else:
        print("No Quotations found.")

import frappe

def execute():
    # Check Procedure records
    print("=== PROCEDURES ===")
    procs = frappe.get_all("Procedure", fields=["name", "patient_name", "quotation"])
    for p in procs:
        print(f"  Procedure {p.name}: patient={p.patient_name}, quotation={p.quotation}")

    # Check Vaccinations records
    print("\n=== VACCINATIONS ===")
    vaccs = frappe.get_all("Vaccinations", fields=["name", "patient_name", "quotation"])
    for v in vaccs:
        print(f"  Vaccination {v.name}: patient={v.patient_name}, quotation={v.quotation}")

    # Check Quotations with custom_patient_name
    print("\n=== QUOTATIONS ===")
    quots = frappe.get_all("Quotation", 
        filters=[["custom_patient_name", "!=", ""]],
        fields=["name", "custom_patient_name", "custom_patient_owner"]
    )
    for q in quots:
        print(f"  Quotation {q.name}: patient={q.custom_patient_name}, owner={q.custom_patient_owner}")

    print("\n=== FIXING: Link orphaned Procedures to Quotations by patient ===")
    fixed = 0
    for p in procs:
        if not p.quotation and p.patient_name:
            # Find a quotation with this patient
            qname = frappe.db.get_value("Quotation", {"custom_patient_name": p.patient_name}, "name", order_by="creation desc")
            if qname:
                frappe.db.set_value("Procedure", p.name, "quotation", qname)
                print(f"  Linked Procedure {p.name} → Quotation {qname}")
                fixed += 1

    print(f"\n=== FIXING: Link orphaned Vaccinations to Quotations by patient ===")
    for v in vaccs:
        if not v.quotation and v.patient_name:
            qname = frappe.db.get_value("Quotation", {"custom_patient_name": v.patient_name}, "name", order_by="creation desc")
            if qname:
                frappe.db.set_value("Vaccinations", v.name, "quotation", qname)
                print(f"  Linked Vaccination {v.name} → Quotation {qname}")
                fixed += 1

    frappe.db.commit()
    print(f"\nTotal fixed: {fixed}")

import frappe

def create_final_test_data():
    # Get next Patient Name ID
    next_id = frappe.db.sql("SELECT COALESCE(MAX(CAST(name AS UNSIGNED)), 0) + 1 FROM `tabPatient Name`;")[0][0]
    
    # Create Patient Name
    pn = frappe.new_doc('Patient Name')
    pn.patient_name = f'TEST-PET-{next_id:03d}'
    pn.patient_owner = 'Test Owner'
    pn.sex = 'Male'
    pn.species = 'Dog'
    pn.breed = 'Labrador'
    pn.colour = 'Black'
    pn.dob = '2020-01-01'
    pn.vaccinated = 1
    pn.next_vaccination_date = '2026-12-01'
    pn.insert()
    frappe.db.commit()
    
    # Create histories with correct fields/names for JS tables
    histories = [
        ('Vaccinations', {'vaccination_date': '2025-01-01'}, 'TEST-VACC-001'),
        ('Procedure', {'doctor_name': 'Administrator', 'procedure_name': 'Checkup', 'start_time': '2026-01-01 10:00:00'}, 'TEST-PROC-001'),
        ('Pet Order', {'diagnosis': 'Routine Exam', 'complaint': 'Wellness check'}, 'TEST-PRES-001'),
        ('Pet Order', {'diagnosis': 'Vaccination Follow-up', 'complaint': 'Post-vaccination', 'order_type': 'Medical Examination'}, 'TEST-MED-001'),
        ('Admissions', {'doctorname': 'Administrator', 'bed_no': 'Bed 101', 'checkin_time': '2026-01-02 09:00', 'checkout_time': '2026-01-02 17:00'}, 'TEST-ADM-001'),
    ]
    
    for doctype, fields, name in histories:
        doc = frappe.new_doc(doctype)
        doc.name = name
        doc.patient_name = pn.name  # Use ID
        for field, value in fields.items():
            doc.set(field, value)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f'Created {doctype} {name}')
    
    print(f'\n\\u2705 COMPLETE. Patient Name: {pn.name}, check Patient Details new → patient_name = {pn.name}')
    print('Tabs: all populated with correct fields/IDs.')

if __name__ == '__main__':
    create_final_test_data()


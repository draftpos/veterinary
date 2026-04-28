import frappe

def create_test_data_v2():
    # Lookups (already done)
    pass

# Patient Name new
pn = frappe.new_doc('Patient Name')
pn.patient_name = 'TEST-PET-003'
pn.patient_owner = 'Test Owner'
pn.sex = 'Male'
pn.species = 'Dog'
pn.breed = 'Labrador'
pn.colour = 'Black'
pn.dob = '2020-01-01'
pn.insert()
frappe.db.commit()

# Histories with reasonable names + fields for JS tables
doctypes = [
    ('Vaccinations', {'vaccination_type': 'Rabies', 'vaccine_name': 'Rabies Vaccine'}),
    ('Procedure', {'doctor_name': 'Administrator', 'procedure_name': 'Annual Checkup', 'start_time': '2026-01-01 10:00'}),
    ('Pet Order', {'diagnosis': 'Routine Check', 'complaint': 'Annual wellness'}),
    ('Pet Order', {'diagnosis': 'Dental Cleaning', 'complaint': 'Teeth issues', 'order_type': 'Medical Examination'}),
    ('Admissions', {'doctor_name': 'Administrator', 'checkin_time': '2026-01-02 09:00', 'checkout_time': '2026-01-03 17:00'}),
]

for dt, fields in doctypes:
    doc = frappe.new_doc(dt)
    doc.name = f'TEST-{dt}-001'
    doc.patient_name = pn.name  # ID
    for k, v in fields.items():
        doc.set(k, v)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    
print('Test data with reasonable names added. Check Patient Details.')

if __name__ == '__main__':
    create_test_data_v2()


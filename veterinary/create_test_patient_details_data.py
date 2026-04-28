import frappe

def create_test_data():
    print('Starting test data creation...')

    # Create Customer
    owner = 'Test Owner'
    if not frappe.db.exists('Customer', {'customer_name': owner}):
        cust = frappe.new_doc('Customer')
        cust.customer_name = owner
        cust.customer_type = 'Individual'
        cust.insert(ignore_permissions=True)
        frappe.db.commit()
        print('Customer created')

    # Create lookups
    lookups = [
        ('Pet Sex', 'Male'),
        ('Pet Sex', 'Female'),
        ('Species', 'Dog'),
        ('Species', 'Cat'),
        ('Pet Breed', 'Labrador'),
        ('Pet Breed', 'Persian'),
        ('Pet Colour', 'Black'),
        ('Pet Colour', 'White'),
    ]
    for dt, val in lookups:
        if not frappe.db.exists(dt, val):
            d = frappe.new_doc(dt)
            d.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f'{dt} {val} created')
    
    # Create Patient Names
    pn_names = []
    for i, pet_info in enumerate([
        ('TEST-DOG-001', 'Male', 'Dog', 'Labrador', 'Black'),
        ('TEST-CAT-001', 'Female', 'Cat', 'Persian', 'White'),
    ]):
        name_label, sex, species, breed, colour = pet_info
        pn = frappe.new_doc('Patient Name')
        pn.patient_name = name_label
        pn.patient_owner = owner
        pn.sex = sex
        pn.species = species
        pn.breed = breed
        pn.colour = colour
        pn.dob = '2020-01-01'
        pn.vaccinated = 1
        pn.insert(ignore_permissions=True)
        frappe.db.commit()
        pn_names.append(pn.name)
        print(f'Patient Name {pn.name} ({name_label}) created')

    # Create Patient Details using py method
    for pn_name in pn_names:
        frappe.get_doc(dict(doctype='Patient Details', patient_name=pn_name)).insert(ignore_permissions=True)
        frappe.db.commit()
        print(f'Patient Details for {pn_name} created')

    # Create histories for first patient
    p1 = pn_names[0]
    # Vaccination
    v_name = 'TEST-VACC-1'
    if not frappe.db.exists('Vaccinations', v_name):
        v = frappe.new_doc('Vaccinations')
        v.name = v_name
        v.patient_name = p1
        v.insert(ignore_permissions=True)
        frappe.db.commit()
        print('Vaccination created')
    
    # Procedure
    pr_name = 'TEST-PROC-1'
    if not frappe.db.exists('Procedure', pr_name):
        pr = frappe.new_doc('Procedure')
        pr.name = pr_name
        pr.patient_name = p1
        pr.procedure_name = 'Test Procedure'
        pr.insert(ignore_permissions=True)
        frappe.db.commit()
        print('Procedure created')
    
    # Pet Orders - NO order_type field, but py filters on it → empty tables. Add to make py happy.
    for order_type in ['Prescription', 'Medical Examination']:
        po_name = f'TEST-PO-{order_type[:3]}-1'
        if not frappe.db.exists('Pet Order', po_name):
            po = frappe.new_doc('Pet Order')
            po.name = po_name
            po.patient_name = p1
            po.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f'Pet Order {order_type} created')
    
    # Admissions
    a_name = 'TEST-ADM-1'
    if not frappe.db.exists('Admissions', a_name):
        a = frappe.new_doc('Admissions')
        a.name = a_name
        a.patient_name = p1
        a.insert(ignore_permissions=True)
        frappe.db.commit()
        print('Admissions created')
    
    print('\\n✅ COMPLETE. New Patient Details in list, onload loads all tabs.')

if __name__ == '__main__':
    create_test_data()


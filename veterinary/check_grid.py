import frappe
frappe.init(site='v15.local')
frappe.connect()

try:
    cf = frappe.get_doc('Custom Field', 'Quotation-custom_pet_details')
    print('Read Only:', cf.read_only)
    print('Hidden:', cf.hidden)
    print('Allow on Submit:', cf.allow_on_submit)
except Exception as e:
    print('Error getting Quotation-custom_pet_details:', e)

try:
    ps = frappe.get_all('Property Setter', filters={'doc_type': 'Quotation', 'field_name': 'custom_pet_details'}, fields=['property', 'value'])
    print('Property Setters for Quotation-custom_pet_details:', ps)
except Exception as e:
    print('Error getting property setters:', e)

try:
    print('Pet Details DocType Properties:')
    meta = frappe.get_meta('Pet Details')
    print('editable_grid:', meta.editable_grid)
    print('istable:', meta.istable)
except Exception as e:
    print('Error getting Pet Details meta:', e)

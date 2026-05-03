import json
import frappe

# First, connect to frappe and delete the fields from the database
frappe.init(site="v15.local", sites_path="/home/ashley/frappe-bench-v15/sites")
frappe.connect()

fields_to_delete = [
    'Quotation-custom_procedures_tab',
    'Quotation-custom_procedure_section',
    'Quotation-custom_procedure_link',
    'Quotation-custom_vaccinations_tab',
    'Quotation-custom_vaccination_section',
    'Quotation-custom_vaccination_link'
]

for field in fields_to_delete:
    if frappe.db.exists("Custom Field", field):
        frappe.delete_doc("Custom Field", field)
        print(f"Deleted {field} from DB")

frappe.db.commit()

# Now remove them from custom_field.json
path = '/home/ashley/frappe-bench-v15/apps/veterinary/veterinary/fixtures/custom_field.json'
with open(path, 'r') as f:
    data = json.load(f)

# The fieldnames
fieldnames = [f.split('-')[1] for f in fields_to_delete]

original_length = len(data)
data = [doc for doc in data if doc.get('fieldname') not in fieldnames]

if len(data) < original_length:
    with open(path, 'w') as f:
        json.dump(data, f, indent=1, separators=(',', ': '))
    print(f"Removed {original_length - len(data)} fields from custom_field.json")
else:
    print("No fields removed from custom_field.json")


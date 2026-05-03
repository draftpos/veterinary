import json
import os

path = '/home/ashley/frappe-bench-v15/apps/veterinary/veterinary/fixtures/custom_field.json'
with open(path, 'r') as f:
    data = json.load(f)

changed = False
for doc in data:
    if doc.get('dt') == 'Quotation' and not doc.get('name'):
        fieldname = doc.get('fieldname')
        doc['name'] = f"Quotation-{fieldname}"
        changed = True

if changed:
    with open(path, 'w') as f:
        json.dump(data, f, indent=1)
    print("Fixtures fixed successfully.")
else:
    print("No fixtures needed fixing.")

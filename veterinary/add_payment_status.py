import json
import frappe

path = '/home/ashley/frappe-bench-v15/apps/veterinary/veterinary/fixtures/custom_field.json'
with open(path, 'r') as f:
    data = json.load(f)

new_fields = [
    {
        "doctype": "Custom Field",
        "name": "Procedure-custom_payment_status",
        "dt": "Procedure",
        "fieldname": "custom_payment_status",
        "fieldtype": "Select",
        "label": "Payment Status",
        "options": "Pending\nPartly Paid\nFully Paid",
        "default": "Pending",
        "read_only": 1,
        "in_list_view": 1,
        "insert_after": "quotation"
    },
    {
        "doctype": "Custom Field",
        "name": "Vaccinations-custom_payment_status",
        "dt": "Vaccinations",
        "fieldname": "custom_payment_status",
        "fieldtype": "Select",
        "label": "Payment Status",
        "options": "Pending\nPartly Paid\nFully Paid",
        "default": "Pending",
        "read_only": 1,
        "in_list_view": 1,
        "insert_after": "quotation"
    },
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_procedure_payment_status",
        "dt": "Quotation",
        "fieldname": "custom_procedure_payment_status",
        "fieldtype": "Select",
        "label": "Procedure Payment Status",
        "options": "Pending\nPartly Paid\nFully Paid",
        "default": "Pending",
        "read_only": 1,
        "in_list_view": 0,
        "insert_after": "custom_procedures_tab"
    },
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_vaccination_payment_status",
        "dt": "Quotation",
        "fieldname": "custom_vaccination_payment_status",
        "fieldtype": "Select",
        "label": "Vaccination Payment Status",
        "options": "Pending\nPartly Paid\nFully Paid",
        "default": "Pending",
        "read_only": 1,
        "in_list_view": 0,
        "insert_after": "custom_vaccinations_tab"
    }
]

# Ensure we don't duplicate
existing_names = [d.get("name") for d in data]
for nf in new_fields:
    if nf["name"] not in existing_names:
        data.append(nf)

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("Custom fields added to custom_field.json")

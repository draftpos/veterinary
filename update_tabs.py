import json
import os

path = '/home/ashley/frappe-bench-v15/apps/veterinary/veterinary/fixtures/custom_field.json'
with open(path, 'r') as f:
    data = json.load(f)

# Identify my fields and any existing sections I might have added
my_fieldnames = [
    'custom_procedures_tab',
    'custom_procedure_section',
    'custom_procedure_link',
    'custom_vaccinations_tab',
    'custom_vaccination_section',
    'custom_vaccination_link'
]

# Remove them first to re-add in clean structure
data = [doc for doc in data if doc.get('fieldname') not in my_fieldnames]

# Define the new sequence
new_fields = [
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_procedures_tab",
        "dt": "Quotation",
        "fieldname": "custom_procedures_tab",
        "fieldtype": "Tab Break",
        "label": "Procedures",
        "insert_after": "connections_tab",
        "show_dashboard": 1
    },
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_procedure_section",
        "dt": "Quotation",
        "fieldname": "custom_procedure_section",
        "fieldtype": "Section Break",
        "label": "Procedure Details",
        "insert_after": "custom_procedures_tab"
    },
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_procedure_link",
        "dt": "Quotation",
        "fieldname": "custom_procedure_link",
        "fieldtype": "Link",
        "label": "Linked Procedure",
        "options": "Procedure",
        "insert_after": "custom_procedure_section",
        "read_only": 1,
        "in_list_view": 1
    },
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_vaccinations_tab",
        "dt": "Quotation",
        "fieldname": "custom_vaccinations_tab",
        "fieldtype": "Tab Break",
        "label": "Vaccinations",
        "insert_after": "custom_procedure_link",
        "show_dashboard": 1
    },
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_vaccination_section",
        "dt": "Quotation",
        "fieldname": "custom_vaccination_section",
        "fieldtype": "Section Break",
        "label": "Vaccination Details",
        "insert_after": "custom_vaccinations_tab"
    },
    {
        "doctype": "Custom Field",
        "name": "Quotation-custom_vaccination_link",
        "dt": "Quotation",
        "fieldname": "custom_vaccination_link",
        "fieldtype": "Link",
        "label": "Linked Vaccinations",
        "options": "Vaccinations",
        "insert_after": "custom_vaccination_section",
        "read_only": 1,
        "in_list_view": 1
    }
]

# Add them back
data.extend(new_fields)

with open(path, 'w') as f:
    json.dump(data, f, indent=1)
print("Fixtures fully updated with sections and list view enabled.")

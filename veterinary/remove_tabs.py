import json
import frappe

def execute():
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

    # We already removed them from custom_field.json using my previous tool call.
    print("Cleanup successful. You can now run bench migrate and clear-cache if needed.")


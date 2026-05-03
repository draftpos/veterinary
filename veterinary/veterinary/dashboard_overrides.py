import frappe

def get_quotation_dashboard_data(data):
    data["transactions"].append({
        "label": "Medical Records",
        "items": ["Pet Order", "Admissions", "Procedure", "Vaccinations"]
    })

    # Frappe's backend uses non_standard_fieldnames to resolve which field on
    # each linked doctype points back to the parent. Without this it falls back
    # to 'prevdoc_docname' which doesn't exist on our custom doctypes.
    if "non_standard_fieldnames" not in data:
        data["non_standard_fieldnames"] = {}

    data["non_standard_fieldnames"].update({
        "Pet Order":    "quotation",
        "Admissions":   "quotation",
        "Procedure":    "quotation",
        "Vaccinations": "quotation",
    })

    return data

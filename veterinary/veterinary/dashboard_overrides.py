import frappe

def get_quotation_dashboard_data(data):
    data["transactions"].append({
        "label": "Medical Records",
        "items": ["Pet Order", "Admissions", "Procedure", "Pet History"]
    })
    return data

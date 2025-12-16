import frappe
from frappe.utils import nowdate
from frappe import _

def execute(filters=None):
    filters = filters or {}
    patient_name = filters.get("patient_name")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not patient_name:
        return [], []

    # Fetch patient details
    patient_list = frappe.get_all(
        "Patient Name",
        filters={"name": patient_name},
        fields=["patient_name", "patient_owner", "colour", "dob", "sex", "species", "breed"],
        limit=1
    )

    if not patient_list:
        print("🔴 No patient found with name:", patient_name)
        return [], [{"visit_date": "No patient found"}]

    print("🟢 Patient details:", patient_list[0])

    # Fetch history
    history = get_pet_history(patient_name, from_date, to_date)
    if not history:
        return [], [{"visit_date": "No visits found"}]

    # Columns for report
    columns = [
        {"label": "Visit Date", "fieldname": "visit_date", "fieldtype": "Date"},
        {"label": "Complaint", "fieldname": "complaint", "fieldtype": "Data"},
        {"label": "Diagnosis", "fieldname": "diagnosis", "fieldtype": "Data"},
        {"label": "Differential Diagnosis", "fieldname": "differential_diagnosis", "fieldtype": "Data"},
        {"label": "Weight", "fieldname": "weight", "fieldtype": "Float"},
        {"label": "HR", "fieldname": "hr", "fieldtype": "Float"},
        {"label": "RR", "fieldname": "rr", "fieldtype": "Float"},
        {"label": "HYD", "fieldname": "hyd", "fieldtype": "Data"},
        {"label": "CRT", "fieldname": "crt", "fieldtype": "Data"},
        {"label": "Items Used", "fieldname": "items_used", "fieldtype": "Data"},
    ]

    return columns, history


def get_pet_history(patient_name, from_date=None, to_date=None):
    # Fetch submitted quotations with the pet details
    conditions = ["po.docstatus=1", "pet.patient_name=%s"]
    values = [patient_name]

    if from_date:
        conditions.append("po.transaction_date >= %s")
        values.append(from_date)
    if to_date:
        conditions.append("po.transaction_date <= %s")
        values.append(to_date)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            po.name AS quotation,
            po.transaction_date AS visit_date,
            pet.complaint,
            pet.diagnosis,
            pet.differential_diagnosis,
            pet.weight,
            pet.hr,
            pet.rr,
            pet.hyd,
            pet.crt,
            GROUP_CONCAT(qi.item_name SEPARATOR ', ') AS items_used
        FROM `tabQuotation` po
        JOIN `tabPet Details` pet
            ON pet.parent = po.name AND pet.parenttype = 'Quotation'
        LEFT JOIN `tabQuotation Item` qi
            ON qi.parent = po.name
        WHERE {where_clause}
        GROUP BY po.name, po.transaction_date, pet.name
        ORDER BY po.transaction_date DESC
    """

    results = frappe.db.sql(query, values, as_dict=True)
    print("🟢 Pet history results:", results)
    return results


# Called by your JS Print button
@frappe.whitelist()
def print_patient_history(filters):
    import json
    from frappe.utils.jinja import render_template

    if isinstance(filters, str):
        filters = json.loads(filters)

    patient_name = filters.get("patient_name")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not patient_name:
        frappe.throw(_("Patient Name is required"))

    # Fetch patient info
    patient_list = frappe.get_all(
        "Patient Name",
        filters={"name": patient_name},
        fields=["patient_name", "patient_owner", "colour", "dob", "sex", "species", "breed"],
        limit=1
    )

    if not patient_list:
        frappe.throw(_("No patient found with name {0}").format(patient_name))

    patient_info = patient_list[0]

    # Fetch history using the same function
    history = get_pet_history(patient_name, from_date, to_date)

    # Render Jinja template
    html = render_template(
        "veterinary/templates/print_patient_history.html",
        {"patient_info": patient_info, "history": history}
    )

    return html

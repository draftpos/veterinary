import frappe
from frappe.utils import nowdate
from frappe import _

def execute(filters=None):
    filters = filters or {}

    patient_owner = filters.get("patient_owner")
    patient_name = filters.get("patient_name")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    follow_up_date = filters.get("follow_up_date")

    history = get_pet_history(
        patient_name=patient_name,
        patient_owner=patient_owner,
        from_date=from_date,
        to_date=to_date,
        follow_up_date=follow_up_date
    )

    columns = [
        {"label": "Visit Date", "fieldname": "visit_date", "fieldtype": "Date"},
        {"label": "Patient", "fieldname": "patient_name", "fieldtype": "Data"},
        {"label": "Owner", "fieldname": "patient_owner", "fieldtype": "Data"},
        {"label": "Complaint", "fieldname": "complaint", "fieldtype": "Data"},
        {"label": "Diagnosis", "fieldname": "diagnosis", "fieldtype": "Data"},
        {"label": "Differential Diagnosis", "fieldname": "differential_diagnosis", "fieldtype": "Data"},
        {"label": "Advices", "fieldname": "advices", "fieldtype": "Data"},
        {"label": "Weight", "fieldname": "weight", "fieldtype": "Float"},
        {"label": "HR", "fieldname": "hr", "fieldtype": "Float"},
        {"label": "RR", "fieldname": "rr", "fieldtype": "Float"},
        {"label": "HYD", "fieldname": "hyd", "fieldtype": "Data"},
        {"label": "CRT", "fieldname": "crt", "fieldtype": "Data"},
        {"label": "Items Used", "fieldname": "items_used", "fieldtype": "Data"},
    ]

    return columns, history

def get_pet_history(patient_name=None, patient_owner=None,follow_up_date=None, from_date=None, to_date=None):
    conditions = ["po.docstatus = 1"]
    values = []

    if patient_name:
        conditions.append("pet.patient_name = %s")
        values.append(patient_name)

    if patient_owner:
        conditions.append("pet.patient_owner = %s")
        values.append(patient_owner)

    if from_date:
        conditions.append("po.transaction_date >= %s")
        values.append(from_date)

    if to_date:
        conditions.append("po.transaction_date <= %s")
        values.append(to_date)

    if follow_up_date:
        conditions.append("po.custom_follow_up_date = %s")
        values.append(follow_up_date)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            po.name AS quotation,
            po.transaction_date AS visit_date,

            -- human-readable patient name
            pn.patient_name AS patient_name,

            pet.patient_owner,
            pet.complaint,
            pet.diagnosis,
            pet.differential_diagnosis,
            pet.advices,
            pet.weight,
            pet.hr,
            pet.rr,
            pet.hyd,
            pet.crt,

            GROUP_CONCAT(qi.item_name SEPARATOR ', ') AS items_used

        FROM `tabQuotation` po

        JOIN `tabPet Details` pet
            ON pet.parent = po.name
            AND pet.parenttype = 'Quotation'

        LEFT JOIN `tabPatient Name` pn
            ON pn.name = pet.patient_name

        LEFT JOIN `tabQuotation Item` qi
            ON qi.parent = po.name

        WHERE {where_clause}

        GROUP BY po.name, po.transaction_date, pet.name
        ORDER BY po.transaction_date DESC
    """

    return frappe.db.sql(query, values, as_dict=True)

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
        fields=["patient_name", "patient_owner", "colour", "dob", "sex", "species", "breed","vaccinated","next_vaccination_date"],
        limit=1
    )
    if not patient_list:
        frappe.throw(_("No patient found with name {0}").format(patient_name))

    patient_info = patient_list[0]

    # Fetch history
    history = get_pet_history(patient_name, from_date, to_date)

    # 👇 Logged-in user
    logged_in_user = frappe.session.user
    logged_in_user_name = frappe.get_value("User", logged_in_user, "full_name")

    html = render_template(
        "veterinary/templates/print_patient_history.html",
        {
            "patient_info": patient_info,
            "history": history,
            "printed_by": logged_in_user_name or logged_in_user
        }
    )

    return html

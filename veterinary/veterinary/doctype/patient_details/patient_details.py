# Copyright (c) 2026, Veterinary Contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PatientDetails(Document):
    """
    One Patient Details record exists per Patient Name record.
    The record name (self.name) IS the Patient Name record's integer id.
    All linked doctypes store that integer in their patient_name field.
    """
    pass


# ---------------------------------------------------------------------------
# Standalone whitelisted function — called from JS via frappe.call
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_patient_history(patient_name):
    """
    Returns all linked history for a patient.
    patient_name = the Patient Name record's name (integer id as string).
    """
    if not patient_name:
        frappe.throw(_('Patient name is required.'))

    return {
        'vaccinations_history': _safe_get_all(
            'Vaccinations',
            {'patient_name': patient_name},
            ['name', 'modified'],
            'modified desc'
        ),
        'procedures_history': _safe_get_all(
            'Procedure',
            {'patient_name': patient_name},
            ['name', 'doctor_name', 'start_time', 'end_time'],
            'start_time desc'
        ),
        # No order_type on Pet Order — both tabs show all Pet Orders for now
        'prescriptions_history': _safe_get_all(
            'Pet Order',
            {'patient_name': patient_name},
            ['name', 'complaint', 'diagnosis', 'modified'],
            'modified desc'
        ),
        'medical_exam_history': _safe_get_all(
            'Pet Order',
            {'patient_name': patient_name},
            ['name', 'complaint', 'diagnosis', 'modified'],
            'modified desc'
        ),
        # Admissions is a child table (istable=1) — cannot query standalone
        'admissions_history': [],
    }


@frappe.whitelist()
def create_patient_details(patient_name):
    """
    Called after a Patient Name record is saved to ensure a
    corresponding Patient Details record exists.
    patient_name = the Patient Name record's integer name.
    """
    if frappe.db.exists('Patient Details', patient_name):
        return {'status': 'exists'}

    doc = frappe.new_doc('Patient Details')
    doc.patient_name = patient_name
    doc.flags.ignore_permissions = True
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_links = True
    doc.insert()
    frappe.db.commit()
    return {'status': 'created', 'name': doc.name}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_get_all(doctype, filters, fields, order_by, limit=50):
    try:
        return frappe.get_all(
            doctype,
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=limit
        )
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f'PatientDetails: failed to load {doctype}'
        )
        return []
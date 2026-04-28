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
        'vaccinations_history': _get_vaccination_details(patient_name),
        'procedures_history': _safe_get_all(
            'Procedure',
            {'patient_name': patient_name},
            ['name', 'doctor_name', 'start_time', 'end_time', 'patient_owner'],
            'start_time desc'
        ),
        'prescriptions_history': _safe_get_all(
            'Pet Order',
            {'patient_name': patient_name},
            ['name', 'complaint', 'diagnosis', 'advices', 'hyd', 'crt', 'weight', 'rr', 'hr', 'modified'],
            'modified desc'
        ),
        'medical_exam_history': _safe_get_all(
            'Pet Order',
            {'patient_name': patient_name},
            ['name', 'complaint', 'diagnosis', 'advices', 'hyd', 'crt', 'weight', 'rr', 'hr', 'modified'],
            'modified desc'
        ),
        'admissions_history': _safe_get_all(
            'Admissions',
            {'patient_name': patient_name},
            ['name', 'bed_no', 'doctorname', 'checkin_time', 'checkout_time'],
            'checkin_time desc'
        ),
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


@frappe.whitelist()
def backfill_all_patient_details():
    """
    Creates a Patient Details record for every Patient Name that doesn't have one.
    Also updates existing records to ensure all fields are in sync.
    Run this once from the console to fix existing records.
    """
    all_patients = frappe.get_all(
        'Patient Name',
        fields=['name', 'patient_name', 'patient_owner', 'sex', 'species',
                'breed', 'colour', 'dob', 'vaccinated', 'next_vaccination_date', 'image']
    )
    created = 0
    updated = 0

    for row in all_patients:
        try:
            if frappe.db.exists('Patient Details', row.name):
                # Update existing — sync all fields
                doc = frappe.get_doc('Patient Details', row.name)
                doc.patient_owner = row.patient_owner
                doc.sex = row.sex
                doc.species = row.species
                doc.breed = row.breed
                doc.colour = row.colour
                doc.dob = row.dob
                doc.vaccinated = row.vaccinated
                doc.next_vaccination_date = row.next_vaccination_date
                doc.image = row.image
                doc.flags.ignore_permissions = True
                doc.save(ignore_permissions=True)
                updated += 1
            else:
                # Create new
                doc = frappe.new_doc('Patient Details')
                doc.patient_name = row.name
                doc.patient_owner = row.patient_owner
                doc.sex = row.sex
                doc.species = row.species
                doc.breed = row.breed
                doc.colour = row.colour
                doc.dob = row.dob
                doc.vaccinated = row.vaccinated
                doc.next_vaccination_date = row.next_vaccination_date
                doc.image = row.image
                doc.flags.ignore_permissions = True
                doc.flags.ignore_mandatory = True
                doc.flags.ignore_links = True
                doc.insert(ignore_permissions=True)
                created += 1
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f'backfill_patient_details: failed for {row.name}'
            )

    frappe.db.commit()
    return {
        'created': created,
        'updated': updated,
        'total': len(all_patients)
    }


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


def _get_vaccination_details(patient_name):
    """
    Fetch all vaccination detail rows for a patient by joining
    Vaccination Detail (child) with Vaccinations (parent).
    """
    try:
        return frappe.db.sql("""
            SELECT
                vd.vaccine,
                vd.batch,
                vd.date,
                vd.user,
                vd.status,
                vd.next_follow_up_date,
                v.name AS vaccination_id
            FROM `tabVaccination Detail` vd
            JOIN `tabVaccinations` v ON v.name = vd.parent
            WHERE v.patient_name = %s
            ORDER BY vd.date DESC
            LIMIT 100
        """, patient_name, as_dict=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            'PatientDetails: failed to load vaccination details'
        )
        return []
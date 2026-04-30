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
        'procedures_history': _get_procedure_history(patient_name),
        'prescriptions_history': _get_prescription_details(patient_name),
        'medical_exam_history': _safe_get_all(
            'Pet Order',
            {'patient_name': patient_name},
            ['name', 'complaint', 'diagnosis', 'advices', 'hyd', 'crt', 'weight', 'rr', 'hr', 'modified'],
            'modified desc'
        ),
        'admissions_history': _get_admissions_history(patient_name),
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


def _get_procedure_history(patient_name):
    """
    Fetch all drugs entered in standalone Procedures by joining
    Drug Detail (child) with Procedure (parent).
    """
    try:
        return frappe.db.sql("""
            SELECT
                p.name,
                p.doctor_name,
                p.start_time,
                p.end_time,
                dd.drug_item,
                dd.quantity,
                dd.dosage,
                dd.instructions
            FROM `tabDrug Detail` dd
            JOIN `tabProcedure` p ON p.name = dd.parent
            WHERE p.patient_name = %s
            ORDER BY p.start_time DESC
            LIMIT 200
        """, patient_name, as_dict=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            'PatientDetails: failed to load procedure history'
        )
        return []


def _get_prescription_details(patient_name):
    """
    Fetch all prescription items for a patient by joining
    Prescription Item (child) with Pet Order (parent).
    """
    try:
        return frappe.db.sql("""
            SELECT
                pi.item_name,
                pi.quantity,
                pi.dosage,
                po.modified as date,
                po.name as order_id
            FROM `tabPrescription Item` pi
            JOIN `tabPet Order` po ON po.name = pi.parent
            WHERE po.patient_name = %s
            ORDER BY po.modified DESC
            LIMIT 200
        """, patient_name, as_dict=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            'PatientDetails: failed to load prescription details'
        )
        return []


def _get_admissions_history(patient_name):
    """
    Fetch all admissions for a patient.
    Uses raw SQL to handle NULL checkin_time for manually created records.
    """
    try:
        return frappe.db.sql("""
            SELECT
                name,
                IFNULL(bed_no, '') as bed_no,
                IFNULL(doctorname, '') as doctorname,
                IFNULL(checkin_time, modified) as checkin_time,
                IFNULL(checkout_time, '') as checkout_time,
                IFNULL(quotation, '') as quotation
            FROM `tabAdmissions`
            WHERE patient_name = %s
            ORDER BY IFNULL(checkin_time, modified) DESC
            LIMIT 100
        """, patient_name, as_dict=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            'PatientDetails: failed to load admissions'
        )
        return []
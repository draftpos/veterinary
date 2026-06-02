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
        'pet_history': _safe_get_all(
            'Pet History',
            {'patient_name': patient_name},
            ['name', 'visit_date', 'weight', 'complaint', 'diagnosis', 'advices'],
            'visit_date desc'
        ),
        'prescriptions_history': _get_prescription_details(patient_name),
        'medical_exam_history': _safe_get_all(
            'Pet Order',
            {'patient_name': patient_name},
            ['name', 'quotation', 'complaint', 'diagnosis', 'advices', 'hyd', 'crt', 'weight', 'rr', 'hr', 'modified'],
            'modified desc'
        ),
        'admissions_history': _get_admissions_history(patient_name),
    }


@frappe.whitelist()
def get_billable_procedures():
    """
    Returns a list of items that are categorized as procedures or services.
    """
    # Check if custom_is_procedure field exists on Item
    if not frappe.db.has_column('Item', 'custom_is_procedure'):
        try:
            from frappe.custom.doctype.custom_field.custom_field import create_custom_field
            create_custom_field('Item', {
                'fieldname': 'custom_is_procedure',
                'label': 'Is Veterinary Procedure',
                'fieldtype': 'Check',
                'insert_after': 'item_name',
                'default': '0',
                'description': 'Mark this item as a veterinary procedure. Only items with this checked will appear in the Billable Procedures list.'
            })
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(message=str(e), title="Failed to create custom field custom_is_procedure")

    # It should exist now, but fallback just in case
    has_custom_field = frappe.db.has_column('Item', 'custom_is_procedure')
    
    filters = {'disabled': 0}
    if has_custom_field:
        filters['custom_is_procedure'] = 1
    else:
        filters['item_group'] = ['in', ['Procedures', 'Services', 'Veterinary Services']]

    return frappe.get_all(
        'Item',
        filters=filters,
        fields=['item_code', 'item_name', 'standard_rate', 'description'],
        order_by='item_name asc'
    )


@frappe.whitelist()
def get_procedure_invoice_data(patient_name):
    """
    Builds a Sales Invoice payload pre-filled with all procedure drugs
    for the given patient. Returns customer + items list only.
    """
    if not patient_name:
        frappe.throw(_('Patient name is required.'))

    # Get patient owner (Customer)
    patient = frappe.db.get_value('Patient Name', patient_name,
                                  ['patient_name', 'patient_owner'], as_dict=True)
    if not patient:
        frappe.throw(_('Patient not found.'))

    customer = patient.patient_owner
    pet_name = patient.patient_name

    # Fetch all procedure records for this patient
    procedures = frappe.get_all(
        'Procedure',
        filters={'patient_name': patient_name},
        fields=['name', 'doctor_name', 'start_time'],
        order_by='start_time desc'
    )

    items = []
    for proc in procedures:
        # Get the drugs in this procedure
        drugs = frappe.get_all(
            'Drug Detail',
            filters={'parent': proc.name},
            fields=['drug_item', 'quantity', 'dosage', 'instructions']
        )
        for drug in drugs:
            if not drug.drug_item:
                continue
            # Fetch the item's price
            rate = frappe.db.get_value('Item', drug.drug_item, 'standard_rate') or 0
            item_name = frappe.db.get_value('Item', drug.drug_item, 'item_name') or drug.drug_item
            items.append({
                'item_code': drug.drug_item,
                'item_name': item_name,
                'qty': drug.quantity or 1,
                'rate': rate,
                'description': f"Pet: {pet_name} | Proc #{proc.name} | Dosage: {drug.dosage or ''} | {drug.instructions or ''}"
            })

    return {
        'customer': customer,
        'pet_name': pet_name,
        'patient_name': patient_name,
        'items': items
    }


@frappe.whitelist()
def get_warehouse_stock():
    """
    Returns stock levels for the Veterinary warehouse.
    """
    company = frappe.db.get_value("Company", {}, "name") or "Veterinary"
    abbr = frappe.db.get_value("Company", company, "abbr") or "V"
    warehouse = f"Veterinary - {abbr}"
    
    if not frappe.db.exists("Warehouse", warehouse):
        return []

    return frappe.db.sql("""
        SELECT 
            bin.item_code, item.item_name, bin.actual_qty, item.stock_uom, item.item_group
        FROM `tabBin` bin
        JOIN `tabItem` item ON item.name = bin.item_code
        WHERE bin.warehouse = %s
          AND bin.actual_qty > 0
        ORDER BY item.item_name ASC
    """, warehouse, as_dict=True)


@frappe.whitelist()
def create_patient_details(patient_name):
    """
    Called after a Patient Name record is saved to ensure a
    corresponding Patient Details record exists.
    patient_name = the Patient Name record's integer name.
    """
    # Search for existing Patient Details using the unique patient_name link field
    existing = frappe.db.get_value('Patient Details', {'patient_name': patient_name}, 'name')
    if existing:
        return {'status': 'exists'}

    doc = frappe.new_doc('Patient Details')
    doc.patient_name = patient_name
    # Pre-fill display name so autoname ({patient_display_name}-{patient_name}) works correctly on insert
    doc.patient_display_name = frappe.db.get_value('Patient Name', patient_name, 'patient_name')
    doc.flags.ignore_permissions = True
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_links = True
    doc.insert()
    frappe.db.commit()
    return {'status': 'created', 'name': doc.name}

@frappe.whitelist()
def migrate_patient_details_urls():
    """
    Renames existing Patient Details records from their formatted names back to plain ID format.
    E.g., "Bruno-3" -> "3". This restores plain IDs (card number-like 1, 2, 3, etc.) as requested.
    """
    import os
    log_file = os.path.join(os.path.dirname(__file__), "migration.log")
    logs = []
    
    records = frappe.get_all('Patient Details', fields=['name', 'patient_name'])
    renamed = 0
    logs.append(f"Found {len(records)} records")
    for r in records:
        logs.append(f"Processing: name='{r.name}', patient_name='{r.patient_name}'")
        # If the name is formatted (e.g. "Bruno-3") and not equal to the patient_name ID (e.g. "3")
        if str(r.name) != str(r.patient_name):
            new_name = str(r.patient_name)
            logs.append(f"  -> Target new name: {new_name}")
            if not frappe.db.exists("Patient Details", new_name):
                try:
                    frappe.rename_doc('Patient Details', r.name, new_name, ignore_permissions=True, force=True)
                    renamed += 1
                    logs.append(f"  -> SUCCESS renamed to {new_name}")
                except Exception as e:
                    frappe.log_error(message=str(e), title=f"Failed to rename Patient Details {r.name}")
                    logs.append(f"  -> FAILED: {str(e)}")
            else:
                logs.append(f"  -> Skipped: new name exists or identical")
    
    if renamed > 0:
        frappe.db.commit()
    
    logs.append(f"Total renamed: {renamed}")
    try:
        with open(log_file, "w") as f:
            f.write("\n".join(logs))
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to write migration log")
        
    return renamed


@frappe.whitelist()
def toggle_reminders(patient_name, stop):
    """
    Toggles vaccination reminders for a patient.
    """
    frappe.db.set_value('Patient Name', patient_name, 'stop_vaccination_reminders', int(stop))
    return {'status': 'success'}


@frappe.whitelist()
def send_vaccination_reminders():
    """
    Job to send reminders for upcoming vaccinations.
    Target: next_follow_up_date in Vaccination Detail.
    """
    from frappe.utils import add_days, getdate, nowdate
    
    # Check for vaccinations due in 3 days and 1 day
    for days_ahead in [3, 1]:
        target_date = add_days(nowdate(), days_ahead)
        
        reminders = frappe.db.sql(f"""
            SELECT 
                vd.vaccine, vd.next_follow_up_date, pn.patient_name, pn.patient_owner, 
                c.email_id, c.mobile_no, pn.name as patient_id
            FROM `tabVaccination Detail` vd
            JOIN `tabVaccinations` v ON v.name = vd.parent
            JOIN `tabPatient Name` pn ON pn.name = v.patient_name
            JOIN `tabCustomer` c ON c.name = pn.patient_owner
            WHERE vd.next_follow_up_date = %s
              AND pn.stop_vaccination_reminders = 0
              AND vd.status != 'Complete'
        """, target_date, as_dict=True)
        
        for r in reminders:
            _send_single_reminder(r, days_ahead)

    return {'status': 'done'}


def _send_single_reminder(data, days_ahead):
    """
    Sends Email, SMS, and WhatsApp placeholders.
    """
    subject = f"Reminder: Vaccination for {data.patient_name} due soon"
    message = f"""
        Dear {data.patient_owner},
        
        This is a reminder that {data.patient_name} is due for their {data.vaccine} 
        vaccination in {days_ahead} day(s) ({data.next_follow_up_date}).
        
        Please visit our clinic to ensure your pet stays healthy.
        
        Regards,
        Veterinary Team
    """
    
    # 1. Email
    if data.email_id:
        try:
            frappe.sendmail(
                recipients=[data.email_id],
                subject=subject,
                message=message
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Vaccination Reminder Email Failed")

    # 2. SMS / WhatsApp (Placeholders)
    # In a real system, you'd call an SMS API here.
    log_msg = f"REMINDER SENT to {data.mobile_no} for {data.patient_name}: {message}"
    frappe.log_error(log_msg, "Vaccination Reminder (SMS/WhatsApp Placeholder)")
    
    # Also create a Communication record for traceability
    comm = frappe.new_doc("Communication")
    comm.communication_type = "Automated Message"
    comm.subject = subject
    comm.content = message
    comm.sender = "Administrator"
    comm.recipients = data.email_id or data.mobile_no
    comm.reference_doctype = "Patient Name"
    comm.reference_name = data.patient_id
    comm.insert(ignore_permissions=True)


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
                'breed', 'colour', 'dob', 'vaccinated', 'next_vaccination_date', 'image', 'patient_card_no']
    )
    created = 0
    updated = 0

    for row in all_patients:
        try:
            existing_name = frappe.db.get_value('Patient Details', {'patient_name': row.name}, 'name')
            if not existing_name and frappe.db.exists('Patient Details', row.name):
                existing_name = row.name

            if existing_name:
                # Update existing — sync all fields
                doc = frappe.get_doc('Patient Details', existing_name)
                doc.patient_owner = row.patient_owner
                doc.patient_card_no = row.patient_card_no
                doc.sex = row.sex
                doc.species = row.species
                doc.breed = row.breed
                doc.colour = row.colour
                doc.dob = row.dob
                doc.vaccinated = row.vaccinated
                doc.next_vaccination_date = row.next_vaccination_date
                doc.image = row.image
                # Set search reference
                doc.search_reference = f"{row.patient_name} - {row.patient_owner}" if row.patient_owner else row.patient_name
                doc.flags.ignore_permissions = True
                doc.save(ignore_permissions=True)
                updated += 1
            else:
                # Create new
                doc = frappe.new_doc('Patient Details')
                doc.patient_name = row.name
                doc.patient_owner = row.patient_owner
                doc.patient_card_no = row.patient_card_no
                doc.sex = row.sex
                doc.species = row.species
                doc.breed = row.breed
                doc.colour = row.colour
                doc.dob = row.dob
                doc.vaccinated = row.vaccinated
                doc.next_vaccination_date = row.next_vaccination_date
                doc.image = row.image
                # Set search reference
                doc.search_reference = f"{row.patient_name} - {row.patient_owner}" if row.patient_owner else row.patient_name
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
                p.quotation,
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
                po.name as order_id,
                po.quotation
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
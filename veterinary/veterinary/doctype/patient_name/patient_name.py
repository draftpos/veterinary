# Copyright (c) 2025, Havano and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PatientName(Document):
    def validate(self):
        """
        Ensure that the combination of patient_name and patient_owner is unique,
        so a customer cannot have two pets with the same name.
        """
        if self.patient_name and self.patient_owner:
            duplicate = frappe.db.exists('Patient Name', {
                'patient_name': self.patient_name,
                'patient_owner': self.patient_owner,
                'name': ['!=', self.name]
            })
            if duplicate:
                frappe.throw(
                    frappe._("A patient named '{0}' already exists for owner '{1}'. Each customer's pet names must be unique.")
                    .format(self.patient_name, self.patient_owner)
                )

    def after_insert(self):
        """
        After a new Patient Name is created, automatically create the
        corresponding Patient Details record.
        """
        self._create_or_refresh_patient_details()

    def on_update(self):
        """
        When Patient Name is updated, refresh the corresponding
        Patient Details record to ensure fetch_from fields are updated.
        Also creates the record if it doesn't exist yet.
        """
        self._create_or_refresh_patient_details()

    def _create_or_refresh_patient_details(self):
        """Create Patient Details if it doesn't exist, otherwise refresh it.
        
        NOTE: fetch_from fields are NOT automatically populated on the backend.
        We must explicitly copy values from Patient Name to Patient Details.
        """
        existing_name = frappe.db.get_value('Patient Details', {'patient_name': self.name}, 'name')
        if not existing_name and frappe.db.exists('Patient Details', self.name):
            existing_name = self.name

        if existing_name:
            details = frappe.get_doc('Patient Details', existing_name)
        else:
            details = frappe.new_doc('Patient Details')
            details.patient_name = self.name

        # Explicitly sync all fetch_from fields (backend doesn't auto-populate these)
        details.patient_card_no = self.patient_card_no
        details.patient_owner = self.patient_owner
        details.sex = self.sex
        details.species = self.species
        details.breed = self.breed
        details.colour = self.colour
        details.dob = self.dob
        details.vaccinated = self.vaccinated
        details.next_vaccination_date = self.next_vaccination_date
        details.image = self.image

        # Update search reference
        details.search_reference = f"{self.patient_name} - {self.patient_owner}" if self.patient_owner else self.patient_name

        details.flags.ignore_permissions = True
        details.flags.ignore_mandatory = True
        details.flags.ignore_links = True

        if details.is_new():
            details.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(
                f"✅ Patient Details record created for {self.patient_name or self.name}",
                indicator="green",
                alert=True,
            )
        else:
            details.save(ignore_permissions=True)

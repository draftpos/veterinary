# Copyright (c) 2025, Havano and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PatientName(Document):
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
        if frappe.db.exists('Patient Details', self.name):
            details = frappe.get_doc('Patient Details', self.name)
        else:
            details = frappe.new_doc('Patient Details')
            details.patient_name = self.name
            is_new = True

        # Explicitly sync all fetch_from fields (backend doesn't auto-populate these)
        details.patient_owner = self.patient_owner
        details.sex = self.sex
        details.species = self.species
        details.breed = self.breed
        details.colour = self.colour
        details.dob = self.dob
        details.vaccinated = self.vaccinated
        details.next_vaccination_date = self.next_vaccination_date
        details.image = self.image

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

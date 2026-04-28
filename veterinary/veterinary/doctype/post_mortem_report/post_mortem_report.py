# Copyright (c) 2025, chirovemunyaradzi@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PostMortemReport(Document):
    def on_submit(self):
        """
        When a post mortem report is submitted, mark the patient as not alive.
        """
        if self.pet_name:
            # Update Patient Name record and trigger its hooks
            patient = frappe.get_doc('Patient Name', self.pet_name)
            patient.alive = 0
            patient.flags.ignore_permissions = True
            patient.save(ignore_permissions=True)
            
            frappe.msgprint(f"Patient {patient.patient_name} has been marked as deceased.")

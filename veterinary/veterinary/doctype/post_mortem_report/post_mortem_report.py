# Copyright (c) 2025, chirovemunyaradzi@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PostMortemReport(Document):
    def before_save(self):
        if self.pet_owner and self.pet_name:
            # These are already the linked doc names (IDs), so we can use them directly
            existing = frappe.get_all(
                "Patient Name",
                filters={
                    "patient_owner": self.patient_owner,   # ID of linked owner
                    "patient_name": self.patient_name, # ID of linked patient
                },
                fields=["name"]
            )
            print(f"--------{self.name}-------------------------exist: {existing}")

            # Untick alive for all matching records
            for doc in existing:
                frappe.db.set_value("Patient Name", doc.name, "alive", 0)

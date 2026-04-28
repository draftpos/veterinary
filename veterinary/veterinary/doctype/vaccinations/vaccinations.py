import frappe
from frappe.model.document import Document

class Vaccinations(Document):
    def on_update(self):
        """
        When a vaccination is recorded, update the master Patient Name record.
        """
        if not self.patient_name:
            return

        # Find the latest next_follow_up_date from child table
        next_date = None
        for row in self.vaccination_details:
            if row.next_follow_up_date:
                if not next_date or row.next_follow_up_date > next_date:
                    next_date = row.next_follow_up_date

        # Update Patient Name record
        patient = frappe.get_doc('Patient Name', self.patient_name)
        patient.vaccinated = 1
        if next_date:
            patient.next_vaccination_date = next_date
        
        patient.flags.ignore_permissions = True
        patient.save(ignore_permissions=True)

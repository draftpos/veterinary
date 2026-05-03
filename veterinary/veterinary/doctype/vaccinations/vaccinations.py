import frappe
from frappe.model.document import Document

class Vaccinations(Document):
    def on_update(self):
        """
        When a vaccination is recorded, update the master Patient Name record
        and sync the payment status back to the linked Quotation.
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

        # Sync payment status to Quotation
        if self.quotation and self.get("custom_payment_status"):
            frappe.db.set_value("Quotation", self.quotation, "custom_vaccination_payment_status", self.custom_payment_status)

    def after_insert(self):
        self.sync_quotation()

    def sync_quotation(self):
        from frappe.utils import today

        if not self.patient_name:
            return

        if self.quotation:
            # Append to existing
            quotation = frappe.get_doc("Quotation", self.quotation)
            if quotation.docstatus != 0:
                frappe.msgprint("Linked Quotation is already submitted/cancelled. Cannot add more items.")
                return
        else:
            # Create new
            quotation = frappe.new_doc("Quotation")
            quotation.quotation_to = "Customer"
            
            patient_owner = frappe.db.get_value("Patient Name", self.patient_name, "patient_owner")
            if not patient_owner:
                frappe.msgprint("Cannot create Quotation: Patient Owner is not set.")
                return
                
            quotation.party_name = patient_owner
            quotation.custom_patient_name = self.patient_name
            quotation.custom_patient_owner = patient_owner

            # Fill inline fields for the Individual view
            quotation.custom_inline_patient_name = self.patient_name
            quotation.custom_inline_patient_owner = patient_owner

            # Fill child table for the Group view
            quotation.append("custom_pet_details", {
                "patient_name": self.patient_name,
                "patient_owner": patient_owner
            })

            quotation.order_type = "Sales"
            quotation.transaction_date = today()
            
            patient_details = frappe.db.get_value("Patient Name", self.patient_name, ["sex", "dob", "colour", "species", "breed"], as_dict=True)
            if patient_details:
                quotation.custom_sex = patient_details.sex
                quotation.custom_date_of_birth = patient_details.dob
                quotation.custom_colour = patient_details.colour
                quotation.custom_species = patient_details.species
                quotation.custom_breed = patient_details.breed

                # Also set inline details
                quotation.custom_inline_sex = patient_details.sex
                quotation.custom_inline_dob = patient_details.dob
                quotation.custom_inline_colour = patient_details.colour
                quotation.custom_inline_species = patient_details.species
                quotation.custom_inline_breed = patient_details.breed

        # No need to set a Link field on the Quotation side (connections handles this)

        # Add items
        has_new_items = False
        if self.vaccination_details:
            for row in self.vaccination_details:
                if row.vaccine:
                    quotation.append("items", {
                        "item_code": row.vaccine,
                        "qty": 1,
                    })
                    has_new_items = True

        if not has_new_items and not self.quotation:
            frappe.msgprint("No vaccines found to add to Quotation.")
            return

        quotation.flags.ignore_permissions = True
        if self.quotation:
            quotation.save(ignore_permissions=True)
            frappe.msgprint(f"Quotation <a href='/app/quotation/{quotation.name}'>{quotation.name}</a> updated with vaccination details.")
        else:
            quotation.insert(ignore_permissions=True)
            self.db_set("quotation", quotation.name)
            frappe.msgprint(f"Quotation <a href='/app/quotation/{quotation.name}'>{quotation.name}</a> automatically created for Vaccinations.")

# Copyright (c) 2026, chirovemunyaradzi@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Procedure(Document):
	def validate(self):
		# Auto-fill patient info from Quotation if not set
		if self.quotation and not self.patient_name:
			details = frappe.db.get_value("Quotation", self.quotation, ["custom_patient_name", "custom_patient_owner"], as_dict=True)
			if details:
				self.patient_name = details.custom_patient_name
				self.patient_owner = details.custom_patient_owner

	def on_update(self):
		# Sync payment status to Quotation
		if self.quotation and self.get("custom_payment_status"):
			frappe.db.set_value("Quotation", self.quotation, "custom_procedure_payment_status", self.custom_payment_status)

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

			patient_owner = self.patient_owner
			if not patient_owner:
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
			
			# Fetch medical exam details if linked
			medical_exam_data = {}
			if self.medical_examination:
				medical_exam_data = frappe.db.get_value("Pet Order", self.medical_examination, 
					["weight", "hyd", "crt", "rr", "hr", "diagnosis", "complaint", "advices", "differential_diagnosis"], 
					as_dict=True) or {}

			# Fill child table for the Group view
			quotation.append("custom_pet_details", {
				"patient_name": self.patient_name,
				"patient_owner": patient_owner,
				"weight": medical_exam_data.get("weight"),
				"hyd": medical_exam_data.get("hyd"),
				"crt": medical_exam_data.get("crt"),
				"rr": medical_exam_data.get("rr"),
				"hr": medical_exam_data.get("hr"),
				"diagnosis": medical_exam_data.get("diagnosis"),
				"complaint": medical_exam_data.get("complaint"),
				"advices": medical_exam_data.get("advices"),
				"differential_diagnosis": medical_exam_data.get("differential_diagnosis")
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


		# Add items
		has_new_items = False
		if self.drugs:
			for row in self.drugs:
				if row.drug_item:
					item_info = frappe.db.get_value("Item", row.drug_item, ["item_name", "stock_uom"], as_dict=True) or {}
					quotation.append("items", {
						"item_code": row.drug_item,
						"item_name": item_info.get("item_name") or row.drug_item,
						"uom": item_info.get("stock_uom") or "Nos",
						"qty": row.quantity or 1,
					})
					has_new_items = True

		if not has_new_items and not self.quotation: # Only add default if creating new and no drugs
			procedure_item = frappe.db.get_value("Item", {"custom_is_procedure": 1}, "name")
			if procedure_item:
				item_info = frappe.db.get_value("Item", procedure_item, ["item_name", "stock_uom"], as_dict=True) or {}
				quotation.append("items", {
					"item_code": procedure_item,
					"item_name": item_info.get("item_name") or procedure_item,
					"uom": item_info.get("stock_uom") or "Nos",
					"qty": 1,
				})
				has_new_items = True

		if not has_new_items and not self.quotation:
			frappe.msgprint("No items found to add to Quotation.")
			return

		quotation.flags.ignore_permissions = True
		if self.quotation:
			quotation.save(ignore_permissions=True)
			if quotation.docstatus == 0:
				quotation.submit()
			frappe.msgprint(f"Quotation <a href='/app/quotation/{quotation.name}'>{quotation.name}</a> updated and submitted with procedure details.")
		else:
			quotation.insert(ignore_permissions=True)
			quotation.submit()
			self.db_set("quotation", quotation.name)
			frappe.db.commit()
			frappe.msgprint(f"Quotation <a href='/app/quotation/{quotation.name}'>{quotation.name}</a> automatically created and submitted for Procedure.")

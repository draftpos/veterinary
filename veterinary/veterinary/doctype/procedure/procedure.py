# Copyright (c) 2026, chirovemunyaradzi@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Procedure(Document):
	def validate(self):
		if self.quotation and not self.patient_name:
			details = frappe.db.get_value("Quotation", self.quotation, ["custom_patient_name", "custom_patient_owner"], as_dict=True)
			if details:
				self.patient_name = details.custom_patient_name
				self.patient_owner = details.custom_patient_owner

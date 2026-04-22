// Copyright (c) 2026, Veterinary Contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Name', {
	after_save(frm) {
		// Auto-create a Patient Details record the first time a Patient Name is saved
		frappe.call({
			method: 'veterinary.veterinary.doctype.patient_details.patient_details.create_patient_details',
			args: { patient_name: frm.doc.name },
			callback(r) {
				if (r.message && r.message.status === 'created') {
					frappe.show_alert({
						message: __('Patient Details record created'),
						indicator: 'green'
					}, 3);
				}
			}
		});
	}
});
// Copyright (c) 2025, chirovemunyaradzi@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pet History', {
	onload(frm) {
		if (frm.is_new() && frm.doc.patient_name) {
			// When created from the dashboard, the patient_name is pre-filled but 
			// fetch_from might not trigger automatically. This forces the fetch.
			setTimeout(() => {
				frm.trigger('patient_name');
			}, 500);
		}
	},

	refresh(frm) {
		if (frm.doc.patient_name) {
			const back_btn_wrapper = frm.get_field('back_to_details_html').$wrapper;
			back_btn_wrapper.empty();
			$('<button class="btn btn-primary" style="margin: 20px;">')
				.html('<i class="fa fa-arrow-left"></i> ' + __('Back to Patient Details Dashboard'))
				.on('click', () => {
					frappe.set_route('Form', 'Patient Details', frm.doc.patient_name);
				})
				.appendTo(back_btn_wrapper);

			// Also add a custom button in the header for convenience
			frm.add_custom_button(__('Patient Dashboard'), () => {
				frappe.set_route('Form', 'Patient Details', frm.doc.patient_name);
			}, __('Actions'));
		}
	}
});

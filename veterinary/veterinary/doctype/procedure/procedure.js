frappe.ui.form.on("Procedure", {
	quotation: function(frm) {
		if (frm.doc.quotation) {
			frappe.db.get_value("Quotation", frm.doc.quotation, ["custom_patient_name", "custom_patient_owner"], (r) => {
				if (r && r.custom_patient_name) {
					frm.set_value("patient_name", r.custom_patient_name);
					frm.set_value("patient_owner", r.custom_patient_owner);
				}
			});
		}
	}
});

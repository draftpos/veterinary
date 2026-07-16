frappe.ui.form.on("Procedure", {
	refresh: function(frm) {
		if (frm.is_new()) {
			frm.set_df_property("quotation", "hidden", 1);
		} else {
			frm.set_df_property("quotation", "read_only", 1);
			frm.set_df_property("quotation", "hidden", 0);
		}
	},
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

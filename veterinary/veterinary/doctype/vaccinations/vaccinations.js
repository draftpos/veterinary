// Copyright (c) 2026, chirovemunyaradzi@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vaccinations", {
	refresh(frm) {
		if (frm.is_new()) {
			frm.set_df_property("quotation", "hidden", 1);
		} else {
			frm.set_df_property("quotation", "read_only", 1);
			frm.set_df_property("quotation", "hidden", 0);
		}
	},
});

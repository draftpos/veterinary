frappe.query_reports["Patient Medical History"] = {
    filters: [
         {
            fieldname: "patient_owner",
            label: "Patient Owner",
            fieldtype: "Link",
            options: "Customer",
        },
        // {
        //     fieldname: "patient_name",
        //     label: "Patient Name",
        //     fieldtype: "Link",
        //     options: "Patient Name",
        // },
         {
            fieldname: "patient_name",
            label: "Patient Name",
            fieldtype: "Link",
            options: "Patient Name",
            get_query: function () {
                const patient_owner = frappe.query_report.get_filter_value("patient_owner");

                if (!patient_owner) {
                    return {};
                }

                return {
                    filters: {
                        patient_owner: patient_owner
                    }
                };
            }
        },
        {
            fieldname: "follow_up_date",
            label: "Follow Up Date",
            fieldtype: "Date"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        }
    ],

    onload: function(report) {
        // Add the Print button
        report.page.add_inner_button("Print History", function() {
            const filters = report.get_values();
            if (!filters) {
                frappe.msgprint("Please select filters first");
                return;
            }

            frappe.call({
                method: "veterinary.veterinary.report.patient_medical_history.patient_medical_history.print_patient_history",
                args: { filters: filters },
                callback: function(r) {
                    if (r.message) {
                        const w = window.open();
                        w.document.write(r.message);  // render Jinja HTML
                        w.document.close();
                        w.print();  // open print dialog
                    }
                }
            });
        });
    }
};

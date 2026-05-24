import frappe

def fix_setup_func():
    doc = frappe.get_doc('Client Script', 'Quotation consolidated')
    script = doc.script

    OLD = """function setup_pet_details_grid(frm) {
    try {
        var grid = frm.fields_dict['custom_pet_details'] && frm.fields_dict['custom_pet_details'].grid;
        if (!grid) return;
        var cols = ['patient_name','patient_owner','sex','date_of_birth','species','breed','colour','follow_up_date','hyd','weight','crt','rr','hr','differential_diagnosis','diagnosis','complaint','advices'];
        grid.visible_columns = undefined;
        cols.forEach(function(fn) {
            var df = frappe.meta.get_docfield("Pet Details", fn);
            if (df) { df.in_list_view = 1; df.hidden = 0; df.read_only = 0; }
        });
        if (!grid.__overridden_edit) {
            grid.edit_row = function(docname) {
                frappe.set_route("Form", "Pet Details", docname);
            };
            grid.__overridden_edit = true;
        }
        grid.refresh();
    } catch(e) {
        console.warn('setup_pet_details_grid error:', e);
    }
}"""

    NEW = """function setup_pet_details_grid(frm) {
    try {
        var grid = frm.fields_dict['custom_pet_details'] && frm.fields_dict['custom_pet_details'].grid;
        if (!grid) return;

        // Only 7 columns in list view so the edit pencil stays visible
        var list_cols = ['patient_name','patient_owner','sex','date_of_birth','species','breed','colour'];
        var all_cols = ['patient_name','patient_owner','sex','date_of_birth','species','breed','colour',
            'follow_up_date','hyd','weight','crt','rr','hr','differential_diagnosis','diagnosis','complaint','advices'];

        all_cols.forEach(function(fn) {
            var df = frappe.meta.get_docfield("Pet Details", fn);
            if (df) {
                df.in_list_view = list_cols.indexOf(fn) !== -1 ? 1 : 0;
                df.hidden = 0;
                df.read_only = 0;
            }
        });

        grid.visible_columns = undefined;
        grid.refresh();
    } catch(e) {
        console.warn('setup_pet_details_grid error:', e);
    }
}"""

    if OLD in script:
        script = script.replace(OLD, NEW)
        doc.script = script
        doc.save()
        frappe.db.commit()
        print("SUCCESS: Updated setup_pet_details_grid.")
    else:
        print("ERROR: Old text not found in script.")
        # Print a portion to help debug
        idx = script.find('function setup_pet_details_grid')
        print("Found at index:", idx)
        print("Snippet:", repr(script[idx:idx+200]))

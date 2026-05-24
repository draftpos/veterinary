import frappe
import json
import os

def update_client_scripts():
    fixture_path = os.path.join(frappe.get_app_path('veterinary'), 'fixtures', 'client_script.json')
    with open(fixture_path, 'r') as f:
        scripts = json.load(f)
    
    for script_data in scripts:
        name = script_data.get('name')
        if name == "Quotation consolidated":
            script = script_data.get('script')
            
            # The script has:
            # frappe.ui.form.on('Pet Details', {
            #     patient_name: function(frm, cdt, cdn) { ... }
            # });
            
            old_str = "frappe.ui.form.on('Pet Details', {"
            new_str = """frappe.ui.form.on('Pet Details', {
    form_render: function(frm, cdt, cdn) {
        // Open in full page when pencil icon is clicked
        setTimeout(function() {
            frappe.set_route("Form", cdt, cdn);
        }, 50);
    },"""
            
            if old_str in script:
                script = script.replace(old_str, new_str)
            
            if frappe.db.exists('Client Script', name):
                doc = frappe.get_doc('Client Script', name)
                doc.script = script
                doc.save()
                print(f"Updated script: {name}")
    
    frappe.db.commit()
    print("Done")

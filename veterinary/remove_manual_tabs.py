import frappe

def execute():
    # Find all Custom Fields on Quotation that have label "Vaccinations" and are Tab Breaks
    fields = frappe.get_all("Custom Field", filters={
        "dt": "Quotation",
        "label": ["in", ["Vaccinations", "vaccinations", "Vaccination", "vaccination"]],
        "fieldtype": "Tab Break"
    }, fields=["name", "fieldname"])

    for f in fields:
        # DO NOT delete the one I created with the status
        if f.fieldname != "custom_vaccinations_tab":
            frappe.delete_doc("Custom Field", f.name)
            print(f"Deleted manual tab: {f.name} ({f.fieldname})")
            
    # Also look for any 'Check' fields inside that tab to clean up orphans
    # (If the tab is deleted, the check field might fall into another tab, so let's delete the check field too if it's named vaccination something)
    check_fields = frappe.get_all("Custom Field", filters={
        "dt": "Quotation",
        "fieldtype": "Check"
    }, fields=["name", "fieldname", "label", "insert_after"])
    
    for c in check_fields:
        if "vaccin" in (c.label or "").lower() or "vaccin" in (c.fieldname or "").lower():
            frappe.delete_doc("Custom Field", c.name)
            print(f"Deleted manual checkbox: {c.name}")

    frappe.db.commit()
    print("Cleanup of manual vaccination tabs and checkboxes complete!")

import frappe

def execute():
    # Find all duplicate/manual Procedure Tab Breaks on Quotation
    fields = frappe.get_all("Custom Field", filters={
        "dt": "Quotation",
        "label": ["in", ["Procedures", "procedures", "Procedure", "procedure"]],
        "fieldtype": "Tab Break"
    }, fields=["name", "fieldname"])

    for f in fields:
        # Keep only the official one we created
        if f.fieldname != "custom_procedures_tab":
            frappe.delete_doc("Custom Field", f.name)
            print(f"Deleted manual tab: {f.name} ({f.fieldname})")

    # Also remove any Check fields related to procedures
    check_fields = frappe.get_all("Custom Field", filters={
        "dt": "Quotation",
        "fieldtype": "Check"
    }, fields=["name", "fieldname", "label"])

    for c in check_fields:
        if "proced" in (c.label or "").lower() or "proced" in (c.fieldname or "").lower():
            frappe.delete_doc("Custom Field", c.name)
            print(f"Deleted manual checkbox: {c.name} ({c.label})")

    frappe.db.commit()
    print("Cleanup of manual procedure tabs and checkboxes complete!")

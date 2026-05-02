import frappe

def create_veterinary_warehouse():
    """
    Creates a separate Warehouse for Veterinary inventory.
    """
    company = frappe.db.get_value("Company", {}, "name") or "Veterinary"
    warehouse_name = "Veterinary"
    
    # ERPNext often appends the company abbreviation, e.g. "Veterinary - V"
    abbr = frappe.db.get_value("Company", company, "abbr") or "V"
    full_warehouse_name = f"{warehouse_name} - {abbr}"
    
    if not frappe.db.exists("Warehouse", full_warehouse_name):
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = warehouse_name
        doc.company = company
        doc.warehouse_type = "Warehouse"
        # Find parent warehouse (usually "All Warehouses - V")
        parent = frappe.db.get_value("Warehouse", {"is_group": 1, "company": company}, "name")
        if parent:
            doc.parent_warehouse = parent
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Created Warehouse: {full_warehouse_name}")
    else:
        print(f"Warehouse already exists: {full_warehouse_name}")

if __name__ == "__main__":
    create_veterinary_warehouse()

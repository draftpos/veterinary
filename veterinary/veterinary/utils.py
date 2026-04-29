import frappe

def before_request():
    if not frappe.cache().get_value("pet_details_schema_synced"):
        try:
            frappe.db.updatedb("Pet Details")
            frappe.db.updatedb("Procedure")
            frappe.cache().set_value("pet_details_schema_synced", 1)
        except Exception:
            pass

@frappe.whitelist(allow_guest=True)
def sync_db():
    try:
        frappe.db.updatedb("Pet Details")
        frappe.db.updatedb("Procedure")
        frappe.db.commit()
        return "Database synced successfully for Pet Details and Procedure."
    except Exception as e:
        return f"Error: {str(e)}"


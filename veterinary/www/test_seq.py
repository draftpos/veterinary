import frappe

def execute():
    frappe.init(site="v15.local")
    frappe.connect()
    try:
        frappe.db.sql("CREATE SEQUENCE IF NOT EXISTS `admissions_id_seq` START WITH 1 INCREMENT BY 1")
        print("Sequence created successfully")
    except Exception as e:
        print(f"Error creating sequence: {e}")
    
    try:
        res = frappe.db.sql("SELECT nextval(`admissions_id_seq`)")
        print(f"Next val: {res}")
    except Exception as e:
        print(f"Error getting next val: {e}")
    frappe.destroy()

if __name__ == "__main__":
    execute()

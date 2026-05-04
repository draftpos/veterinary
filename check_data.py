import frappe

def check_data():
    doctypes = ["Procedure", "Vaccinations", "Pet Order", "Admissions"]
    for dt in doctypes:
        try:
            count = frappe.db.count(dt)
            print(f"{dt}: {count} records")
            if count > 0:
                sample = frappe.get_all(dt, limit=1, fields=["name", "patient_name", "quotation"])
                print(f"  Sample: {sample}")
        except Exception as e:
            print(f"Error checking {dt}: {e}")

if __name__ == "__main__":
    check_data()

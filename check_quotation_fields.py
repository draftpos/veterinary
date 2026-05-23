import frappe

def main():
    frappe.init("v15.local", sites_path="/home/ashley/frappe-bench-v15/sites")
    frappe.connect()
    
    custom_fields = frappe.get_all("Custom Field", filters={"dt": "Quotation"}, fields=["fieldname", "label", "fieldtype"])
    for cf in custom_fields:
        print(f"Quotation Custom Field: {cf.fieldname} ({cf.label}) - {cf.fieldtype}")

if __name__ == "__main__":
    main()

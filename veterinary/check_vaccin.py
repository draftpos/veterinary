import frappe
frappe.init(site="v15.local", sites_path="/home/ashley/frappe-bench-v15/sites")
frappe.connect()

fields = frappe.get_all("Custom Field", filters={"fieldname": ["like", "%vaccin%"], "dt": "Quotation"}, fields=["name", "fieldname", "fieldtype", "label"])
for f in fields:
    print(f"{f.name} - {f.fieldname} - {f.fieldtype} - {f.label}")

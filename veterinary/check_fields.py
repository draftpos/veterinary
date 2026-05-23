import json
path = "/home/ashley/frappe-bench-v15/apps/veterinary/veterinary/veterinary/doctype/pet_details/pet_details.json"
with open(path, "r") as f: data = json.load(f)
for field in data["fields"]:
    if field.get("fieldtype") not in ["Section Break", "Column Break", "Tab Break"] and not field.get("in_list_view"):
        print(field.get("fieldname"), field.get("fieldtype"))

import json
path = "/home/ashley/frappe-bench-v15/apps/veterinary/veterinary/veterinary/doctype/pet_details/pet_details.json"
with open(path, "r") as f: data = json.load(f)
for field in data["fields"]:
    if field.get("fieldtype") == "Table":
        field["hidden"] = 1
with open(path, "w") as f: json.dump(data, f, indent=1, ensure_ascii=False)

import json
import re

path = "/home/ashley/frappe-bench-v15/apps/veterinary/veterinary/fixtures/client_script.json"
with open(path, "r") as f:
    data = json.load(f)

for item in data:
    if item.get("name") == "Quotation consolidated":
        script = item["script"]
        if "setup_grid_create_new" in script:
            script = re.sub(r"function setup_grid_create_new.*?}\n}\n", "", script, flags=re.DOTALL)
            script = script.replace("setup_grid_create_new(frm);", "")
            item["script"] = script
            print("Removed setup_grid_create_new")

with open(path, "w") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)

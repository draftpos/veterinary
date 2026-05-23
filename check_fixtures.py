import json

with open('veterinary/fixtures/custom_field.json', 'r') as f:
    data = json.load(f)

# Check for entries missing 'name' field
for i, doc in enumerate(data):
    if 'name' not in doc:
        print(f'Entry at index {i} missing name:')
        print(f'  doctype: {doc.get("doctype")}')
        print(f'  keys: {list(doc.keys())}')
        print(f'  content: {str(doc)[:500]}')
        print()

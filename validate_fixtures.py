import json

# Validate custom_field.json
try:
    with open('veterinary/fixtures/custom_field.json', 'r') as f:
        data = json.load(f)
    print(f'custom_field.json: Valid JSON with {len(data)} entries')
    
    # Check for entries missing 'name' field
    missing_name = []
    for i, doc in enumerate(data):
        if 'name' not in doc:
            missing_name.append((i, doc.get('doctype'), doc.get('dt'), doc.get('fieldname')))
    
    if missing_name:
        print(f'WARNING: {len(missing_name)} entries missing name field:')
        for idx, dt, dt_name, fieldname in missing_name:
            print(f'  Index {idx}: {dt}.{dt_name}.{fieldname}')
    else:
        print('All entries have name field')
except json.JSONDecodeError as e:
    print(f'JSON Error: {e}')
except Exception as e:
    print(f'Error: {e}')

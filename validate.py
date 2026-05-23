#!/usr/bin/env python3
"""
Validate custom_field.json for issues.
"""
import json
import re

filepath = 'veterinary/veterinary/fixtures/custom_field.json'

print(f"Reading {filepath}...")

try:
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Try to parse
    data = json.loads(content)
    print(f"JSON is valid! Found {len(data)} entries.")
    
    # Check for entries missing 'name' field
    missing_name = []
    for i, doc in enumerate(data):
        if 'name' not in doc:
            missing_name.append((i, doc.get('doctype'), doc.get('dt'), doc.get('fieldname')))
    
    if missing_name:
        print(f"\n⚠️  Found {len(missing_name)} entries missing 'name' field:")
        for idx, doctype, dt, fieldname in missing_name[:5]:
            print(f"  - Index {idx}: doctype={doctype}, dt={dt}, fieldname={fieldname}")
    else:
        print("\n✅ All entries have 'name' field.")
        
except json.JSONDecodeError as e:
    print(f"❌ JSON Error at line {e.lineno}, column {e.colno}: {e.msg}")
    
    # Show context
    lines = content.split('\n')
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    for i in range(start, end):
        prefix = ">>> " if i == e.lineno - 1 else "    "
        print(f"{prefix}{i+1}: {lines[i]}")

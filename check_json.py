#!/usr/bin/env python3
import json
import sys

filepath = 'veterinary/veterinary/fixtures/custom_field.json'

try:
    with open(filepath, 'r') as f:
        content = f.read()
        # Try to parse and show exact error location
        json.loads(content)
    print("JSON is valid!")
except json.JSONDecodeError as e:
    print(f"JSON Error at line {e.lineno}, column {e.colno} (char {e.pos})")
    print(f"Message: {e.msg}")
    
    # Show context around error
    lines = content.split('\n')
    if e.lineno <= len(lines):
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        for i in range(start, end):
            prefix = ">>> " if i == e.lineno - 1 else "    "
            print(f"{prefix}{i+1}: {lines[i]}")

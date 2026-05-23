# Read specific lines around line 3080
with open('veterinary/veterinary/fixtures/custom_field.json', 'r') as f:
    lines = f.readlines()

# Print lines 3070-3090 (0-indexed: 3069-3089)
start = max(0, 3069)
end = min(len(lines), 3090)
for i in range(start, end):
    print(f"{i+1}: {lines[i]}", end='')

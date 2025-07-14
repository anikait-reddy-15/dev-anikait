import os
import json

# Directory to save the files (change if needed)
output_dir = "C:\Work Repos\JSON Outputs Planner"
os.makedirs(output_dir, exist_ok=True)

# Generate empty JSON files from Q1001 to Q5000
for i in range(1001, 5001):
    filename = f"Q{i}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({}, f, indent=4)

print(f"Generated {5000 - 1000} empty JSON files in '{output_dir}' directory.")

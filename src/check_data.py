import json
from pathlib import Path

raw_folder = Path("data/raw")

patch_counts = {}

for match_file in raw_folder.glob("*_match.json"):
    with open(match_file, "r", encoding="utf-8") as file:
        match_data = json.load(file)
    version = match_data["info"]["gameVersion"]
    parts = version.split(".")
    patch = parts[0] + "." + parts[1]
    if patch not in patch_counts:
        patch_counts[patch] = 0
    patch_counts[patch] += 1
print("Matches by Patch")
print("----------------")

for patch in sorted(patch_counts):
    print(patch, ":", patch_counts[patch])

print()
print("Total Matches:", sum(patch_counts.values()))
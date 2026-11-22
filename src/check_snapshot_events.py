import csv
import json
from pathlib import Path

with open("data/processed/match_features.csv", "r") as file:
    rows = list(csv.DictReader(file))

important_events = [
    "CHAMPION_KILL",
    "CHAMPION_SPECIAL_KILL",
    "ELITE_MONSTER_KILL",
    "BUILDING_KILL"
]

event_counts = {}
affected_rows = set()

for row in rows:

    match_id = row["match_id"]
    minute = int(row["minute"])

    target_time = minute * 60000
    snapshot_time = int(row["timestamp"])

    timeline_file = Path("data/raw") / f"{match_id}_timeline.json"

    with open(timeline_file, "r") as file:
        timeline = json.load(file)

    for frame in timeline["info"]["frames"]:
        for event in frame.get("events", []):

            event_type = event.get("type")
            event_time = event.get("timestamp")

            if event_time is None:
                continue

            if event_type not in important_events:
                continue

            if target_time < event_time <= snapshot_time:

                if event_type not in event_counts:
                    event_counts[event_type] = 0

                event_counts[event_type] += 1
                affected_rows.add((match_id, minute))

print()
print("SNAPSHOT EVENT CHECK")
print("---------------------------")
print("Rows checked:", len(rows))
print("Rows with events after exact cutoff:", len(affected_rows))

print()
print("Events between exact minute and selected snapshot:")

for event_type in important_events:
    count = event_counts.get(event_type, 0)
    print(event_type, ":", count)
import csv
import json
from pathlib import Path

with open("data/processed/match_features.csv", "r") as file:
    rows = list(csv.DictReader(file))

match_ids = set()

for row in rows:
    match_ids.add(row["match_id"])

zero_events = {}
total_zero = 0
missing = 0

important_events = [
    "CHAMPION_KILL",
    "CHAMPION_SPECIAL_KILL",
    "ELITE_MONSTER_KILL",
    "BUILDING_KILL"
]

important_zero = 0

for match_id in match_ids:

    timeline_file = Path("data/raw") / f"{match_id}_timeline.json"

    with open(timeline_file, "r") as file:
        timeline = json.load(file)

    for frame in timeline["info"]["frames"]:
        for event in frame.get("events", []):

            timestamp = event.get("timestamp")
            event_type = event.get("type", "UNKNOWN")

            if timestamp is None:
                missing += 1

            elif timestamp == 0:

                total_zero += 1

                if event_type not in zero_events:
                    zero_events[event_type] = 0

                zero_events[event_type] += 1

                if event_type in important_events:
                    important_zero += 1
                    print("Important zero event:", match_id, event_type)

print()
print("ZERO TIMESTAMP CHECK")
print("---------------------------")
print("Matches checked:", len(match_ids))
print("Missing timestamps:", missing)
print("Total zero timestamps:", total_zero)

print()
print("Zero timestamps by event type:")

for event_type in sorted(zero_events):
    print(event_type, ":", zero_events[event_type])

print()
print("Important events at timestamp zero:", important_zero)
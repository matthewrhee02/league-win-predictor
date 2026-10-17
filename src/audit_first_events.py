import csv
import json
from pathlib import Path

with open("data/processed/match_features.csv", "r") as file:
    rows = list(csv.DictReader(file))

mistakes = 0

for row in rows:
    match_id = row["match_id"]
    minute = int(row["minute"])
    timestamp = int(row["timestamp"])
    timeline_file = Path("data/raw") / f"{match_id}_timeline.json"
    with open(timeline_file, "r") as file:
        timeline = json.load(file)
    
    events = []

    for frame in timeline["info"]["frames"]:
        for event in frame.get("events", []):
            if event.get("timestamp", 0) <= timestamp:
                events.append(event)
    events.sort(key=lambda event: event.get("timestamp", 0))

    first_blood = 0
    first_tower = 0
    first_dragon = 0
    found_blood = False
    found_tower = False
    found_dragon = False

    for event in events:
        event_type = event.get("type")
        if event_type == "CHAMPION_KILL" and not found_blood:
            killer = event.get("killerId", 0)
            if 1 <= killer <= 5:
                first_blood = 1
                found_blood = True
            elif 6 <= killer <= 10:
                first_blood = -1
                found_blood = True
        if event_type == "BUILDING_KILL" and not found_tower:
            if event.get("buildingType") == "TOWER_BUILDING":
                found_tower = True
                destroyed_team = event.get("teamId")
                if destroyed_team == 200:
                    first_tower = 1
                elif destroyed_team == 100:
                    first_tower = -1
        if event_type == "ELITE_MONSTER_KILL" and not found_dragon:
            if event.get("monsterType") == "DRAGON":
                found_dragon = True
                team = event.get("killerTeamId")
                if team == 100:
                    first_dragon = 1
                elif team == 200:
                    first_dragon = -1

    expected = {
        "first_blood": first_blood,
        "first_tower": first_tower,
        "first_dragon": first_dragon,
    }

    for feature in expected:
        actual = int(row[feature])
        if actual != expected[feature]:
            mistakes += 1
            if mistakes <= 10:
                print("Mismatch:", match_id, minute, feature)
                print("CSV value:", actual)
                print("Expected value:", expected[feature])

print()
print("FIRST EVENT AUDIT")
print("---------------------------")
print("Rows checked:", len(rows))
print("Feature mismatches:", mistakes)
print()
print("FIRST EVENT COUNTS BY MINUTE")
print("---------------------------")

for minute in [5, 10, 15]:
    print()
    print("Minute:", minute)

    for feature in ["first_blood", "first_tower", "first_dragon"]:
        count = 0
        total = 0
        for row in rows:
            if int(row["minute"]) == minute:
                total += 1
                if int(row[feature]) != 0:
                    count += 1
        print(feature + ":", count, "out of", total)
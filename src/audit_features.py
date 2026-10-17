import csv
import json
from pathlib import Path

with open("data/processed/match_features.csv", "r") as file:
    rows = list(csv.DictReader(file))

checked = 0
mistakes = 0
after_target = 0
before_target = 0
largest_difference = 0

for row in rows:
    match_id = row["match_id"]
    minute = int(row["minute"])
    timestamp = int(row["timestamp"])
    target_time = minute * 60000
    difference = timestamp - target_time
    if difference > 0:
        after_target += 1
    elif difference < 0:
        before_target += 1
    if abs(difference) > largest_difference:
        largest_difference = abs(difference)

    timeline_file = Path("data/raw") / f"{match_id}_timeline.json"
    
    with open(timeline_file, "r") as file:
        timeline = json.load(file)

    frames = timeline["info"]["frames"]
    selected_frame = None
    for frame in frames:
        if frame["timestamp"] == timestamp:
            selected_frame = frame
            break
    if selected_frame is None:
        print("Missing frame:", match_id, minute)
        mistakes += 1
        continue

    expected = {
        "gold_diff": 0,
        "xp_diff": 0,
        "cs_diff": 0,
        "jungle_cs_diff": 0,
        "kill_diff": 0,
        "tower_diff": 0,
        "dragon_diff": 0,
        "grub_diff": 0
    }

    for participant_id, player in selected_frame["participantFrames"].items():
        if int(participant_id) <= 5:
            team = 1
        else:
            team = -1

        expected["gold_diff"] += team * player.get("totalGold", 0)
        expected["xp_diff"] += team * player.get("xp", 0)
        expected["cs_diff"] += team * player.get("minionsKilled", 0)
        expected["jungle_cs_diff"] += team * player.get("jungleMinionsKilled", 0)

    for frame in frames:
        for event in frame.get("events", []):
            if event.get("timestamp", 0) > timestamp:
                continue
            event_type = event.get("type")
            if event_type == "CHAMPION_KILL":
                killer = event.get("killerId", 0)
                if 1 <= killer <= 5:
                    expected["kill_diff"] += 1
                elif 6 <= killer <= 10:
                    expected["kill_diff"] -= 1
            elif event_type == "ELITE_MONSTER_KILL":
                monster = event.get("monsterType")
                team = event.get("killerTeamId")
                if team == 100:
                    value = 1
                elif team == 200:
                    value = -1
                else:
                    value = 0
                if monster == "DRAGON":
                    expected["dragon_diff"] += value
                elif monster == "HORDE":
                    expected["grub_diff"] += value
            elif event_type == "BUILDING_KILL":
                if event.get("buildingType") == "TOWER_BUILDING":
                    destroyed_team = event.get("teamId")
                    if destroyed_team == 200:
                        expected["tower_diff"] += 1
                    elif destroyed_team == 100:
                        expected ["tower_diff"] -= 1

    for feature in expected:
        actual = int(row[feature])
        if actual != expected[feature]:
            mistakes += 1
            if mistakes < 10:
                print("Mismatch:", match_id, minute, feature)
                print("CSV value:", actual)
                print("JSON value:", expected[feature])
    checked += 1
print()
print("FEATURE AUDIT")
print("---------------------------")
print("Rows checked:", checked)
print("Feature mismatches:", mistakes)
print("Snapshots after target:", after_target)
print("Snapshots before target:", before_target)
print("Largest time difference:", largest_difference, "ms")

if mistakes == 0:
    print("All checked features match the raw timeline")
else:
    print("Some features need to be investigated.")
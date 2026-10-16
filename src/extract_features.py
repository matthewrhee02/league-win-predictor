import csv
import json
from pathlib import Path

raw_folder = Path("data/raw")
processed_folder = Path("data/processed")
processed_folder.mkdir(parents=True, exist_ok=True)

rows = []

for match_file in sorted(raw_folder.glob("*_match.json")):
    match_id = match_file.name.replace("_match.json", "")
    timeline_file = raw_folder / f"{match_id}_timeline.json"
    if not timeline_file.exists():
        print("Missing timeline:", match_id)
        continue
    with open(match_file, "r", encoding="utf-8") as file:
        match_data = json.load(file)
    version = match_data["info"].get("gameVersion", "")
    parts = version.split(".")
    patch = parts[0] + "." + parts[1]
    if patch != "16.20":
        print("Skipping older patch:", match_id)
        continue
    with open(timeline_file, "r", encoding="utf-8") as file:
        timeline_data = json.load(file)

    blue_win = None

    for team in match_data["info"]["teams"]:
        if team["teamId"] == 100:
            blue_win = int(team["win"])
    if blue_win is None:
        continue
    frames = timeline_data["info"]["frames"]

    for minute in [5, 10, 15]:
        target_time = minute * 60 * 1000
        closest_frame = None
        smallest_difference = float("inf")
        for frame in frames:
            difference = abs(frame["timestamp"] - target_time)
            if difference < smallest_difference:
                smallest_difference = difference
                closest_frame = frame
        if closest_frame is None or smallest_difference > 30000:
            print("missing", minute, "minute frame:", match_id)
            continue

        blue_kills = 0
        red_kills = 0
        blue_towers = 0
        red_towers = 0
        blue_dragons = 0
        red_dragons = 0
        blue_grubs = 0
        red_grubs = 0
        first_blood = 0
        first_tower = 0
        first_dragon = 0
        for event_frame in frames:
            for event in event_frame.get("events", []):
                if event.get("timestamp", 0) > closest_frame["timestamp"]:
                    continue
                event_type = event.get("type")
                if event_type == "CHAMPION_KILL":
                    killer = event.get("killerId", 0)
                    if 1 <= killer <= 5:
                        blue_kills += 1
                    elif 6 <= killer <= 10:
                        red_kills += 1
                if event_type == "CHAMPION_SPECIAL_KILL":
                    if event.get("killType") == "KILL_FIRST_BLOOD":
                        killer = event.get("killerId", 0)
                        if 1 <= killer <= 5:
                            first_blood = 1
                        elif 6 <= killer <= 10:
                            first_blood = -1
                if event_type == "ELITE_MONSTER_KILL":
                    monster = event.get("monsterType")
                    team = event.get("killerTeamId")
                    if monster == "DRAGON":
                        if first_dragon == 0:
                            if team == 100:
                                first_dragon = 1
                            elif team == 200:
                                first_dragon = -1
                        if team == 100:
                            blue_dragons += 1
                        elif team == 200:
                            red_dragons += 1
                    elif monster == "HORDE":
                        if team == 100:
                            blue_grubs += 1
                        elif team == 200:
                            red_grubs += 1
                if event_type == "BUILDING_KILL":
                    if event.get("buildingType") == "TOWER_BUILDING":
                        destroyed_team = event.get("teamId")
                        if destroyed_team == 200:
                            blue_towers += 1
                            if first_tower == 0:
                                first_tower = 1
                        elif destroyed_team == 100:
                            red_towers += 1
                            if first_tower == 0:
                                first_tower = -1

        participant_frames = closest_frame["participantFrames"]

        blue_gold = 0
        red_gold = 0
        blue_xp = 0
        red_xp = 0
        blue_cs = 0
        red_cs = 0
        blue_jungle_cs = 0
        red_jungle_cs = 0

        for participant_id, player in participant_frames.items():
            gold = player.get("totalGold", 0)
            xp = player.get("xp", 0)
            cs = player.get("minionsKilled", 0)
            jungle_cs = player.get("jungleMinionsKilled", 0)
            if int(participant_id) <= 5:
                blue_gold += gold
                blue_xp += xp
                blue_cs += cs
                blue_jungle_cs += jungle_cs
            else:
                red_gold += gold
                red_xp += xp
                red_cs += cs
                red_jungle_cs += jungle_cs
        rows.append({
            "match_id": match_id,
            "minute": minute,
            "timestamp": closest_frame["timestamp"],
            "gold_diff": blue_gold - red_gold,
            "xp_diff": blue_xp - red_xp,
            "cs_diff": blue_cs - red_cs,
            "jungle_cs_diff": blue_jungle_cs - red_jungle_cs,
            "kill_diff": blue_kills - red_kills,
            "tower_diff": blue_towers - red_towers,
            "dragon_diff": blue_dragons - red_dragons,
            "grub_diff": blue_grubs - red_grubs,
            "first_blood": first_blood,
            "first_tower": first_tower,
            "first_dragon": first_dragon,
            "blue_win": blue_win
        })
    print("Procesed:", match_id)
output_file = processed_folder / "match_features.csv"
with open(output_file, "w", newline="", encoding="utf-8") as file:
    columns = [
        "match_id",
        "minute",
        "timestamp",
        "gold_diff",
        "xp_diff",
        "cs_diff",
        "jungle_cs_diff",
        "kill_diff",
        "tower_diff",
        "dragon_diff",
        "grub_diff",
        "first_blood",
        "first_tower",
        "first_dragon",
        "blue_win"
    ]
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print()
print("Finished extracting features.")
print("Total rows:", len(rows))
print("Saved to:", output_file)
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
        "blue_win"
    ]
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print()
print("Finished extracting features.")
print("Total rows:", len(rows))
print("Saved to:", output_file)
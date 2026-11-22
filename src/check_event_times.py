import csv
import json
from pathlib import Path

with open("data/processed/match_features.csv", "r") as file:
    rows = list(csv.DictReader(file))

match_ids = set()

for row in rows:
    match_ids.add(row["match_id"])

blood_times = []
dragon_times = []

missing_timestamps = 0
zero_timestamps = 0

for match_id in match_ids:

    timeline_file = Path("data/raw") / f"{match_id}_timeline.json"

    with open(timeline_file, "r") as file:
        timeline = json.load(file)

    first_blood = None
    first_dragon = None

    for frame in timeline["info"]["frames"]:
        for event in frame.get("events", []):

            event_type = event.get("type")
            timestamp = event.get("timestamp")

            if timestamp is None:
                missing_timestamps += 1
                continue

            if timestamp == 0:
                zero_timestamps += 1

            if event_type == "CHAMPION_SPECIAL_KILL":
                if event.get("killType") == "KILL_FIRST_BLOOD":

                    if first_blood is None or timestamp < first_blood:
                        first_blood = timestamp

            if event_type == "ELITE_MONSTER_KILL":
                if event.get("monsterType") == "DRAGON":

                    if first_dragon is None or timestamp < first_dragon:
                        first_dragon = timestamp

    if first_blood is not None:
        blood_times.append(first_blood)

    if first_dragon is not None:
        dragon_times.append(first_dragon)

print("EVENT TIMESTAMP CHECK")
print("---------------------------")
print("Matches checked:", len(match_ids))
print("Missing timestamps:", missing_timestamps)
print("Zero timestamps:", zero_timestamps)

events = {
    "First Blood": blood_times,
    "First Dragon": dragon_times
}

for name, times in events.items():

    times.sort()

    print()
    print(name)
    print("Events found:", len(times))

    if len(times) > 0:

        print("Earliest minute:", round(times[0] / 60000, 2))
        print("Median minute:", round(times[len(times) // 2] / 60000, 2))
        print("Latest minute:", round(times[-1] / 60000, 2))

        for minute in [5, 10, 15]:

            count = 0

            for timestamp in times:
                if timestamp <= minute * 60000:
                    count += 1

            print("By minute", minute, ":", count)
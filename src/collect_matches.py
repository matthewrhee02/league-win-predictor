import csv
import json
import random
import time
from pathlib import Path
from getpass import getpass
import requests

REGION = "https://americas.api.riotgames.com"
PLATFORM = "https://na1.api.riotgames.com"
TIERS = ["GOLD", "PLATINUM", "EMERALD", "DIAMOND"]
MATCHES_PER_TIER = 50
SEEDS_PER_TIER = 60
MATCHES_PER_SEED = 3
TARGET_PATCH = "16.20"

data_folder = Path("data/raw")
data_folder.mkdir(parents=True, exist_ok=True)

api_key = getpass("Enter your Riot API key: ")

headers = {
    "X-Riot-Token": api_key
}

def get_data(url, params=None):
    for attempt in range(5):
        time.sleep(1.5)
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
        except requests.RequestException:
            print("Conection failed. Retrying...")
            time.sleep(5)
            continue
        if response.status_code == 429:
            wait = float(response.headers.get("Retry-After", 10))
            print("Rate limit reached. Waiting", wait, "seconds")
            time.sleep(wait + 1)
            continue
        if response.status_code in [401, 403]:
            print("API key rejeected. Check your Riot API key.")
            raise SystemExit
        if response.status_code in [500, 502, 503, 504]:
            print("Riot server error. Retrying...")
            time.sleep(5)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Request failed after multiple attempts.")

checked_matches = set()
total_downloaded = 0
rng = random.Random(42)

for tier in TIERS:
    print()
    print("=" * 50)
    print("Collecting matches from", tier)
    print("=" * 50)

    seed_players = []
    found_players = set()

    for page in [1, 2, 3]:
        ranked_url = (
            f"{PLATFORM}/lol/league/v4/entries/"
            f"RANKED_SOLO_5x5/{tier}/IV"
        )
        entries = get_data(ranked_url, {"page": page})
        for entry in entries:
            puuid = entry.get("puuid")
            if puuid and puuid not in found_players:
                seed_players.append(puuid)
                found_players.add(puuid)
    rng.shuffle(seed_players)

    print("Found", len(seed_players), "possible seed players")
    tier_downloaded = 0

    for puuid in seed_players[:SEEDS_PER_TIER]:
        if tier_downloaded >= MATCHES_PER_TIER:
            break
        matches_url = (
            f"{REGION}/lol/match/v5/matches/"
            f"by-puuid/{puuid}/ids"
        )
        params = {
            "queue": 420,
            "start": 0,
            "count": 20
        }

        match_ids = get_data(matches_url, params)
        seed_downloaded = 0
        for match_id in match_ids:
            if tier_downloaded >= MATCHES_PER_TIER:
                break
            if seed_downloaded>= MATCHES_PER_SEED:
                break
            if match_id in checked_matches:
                continue
            checked_matches.add(match_id)

            match_file = data_folder / f"{match_id}_match.json"
            timeline_file = data_folder / f"{match_id}_timeline.json"

            if match_file.exists() and timeline_file.exists():
                print("Already saved:", match_id)
                continue
            match_url = (
                f"{REGION}/lol/match/v5/matches/{match_id}"
            )
            timeline_url = (
                f"{REGION}/lol/match/v5/matches/"
                f"{match_id}/timeline"
            )
            try:
                match_data = get_data(match_url)
            except requests.HTTPError as error:
                if error.response.status_code == 404:
                    print("Match not found:", match_id)
                    continue
                raise

            info = match_data["info"]
            if info.get("queueId") != 420:
                continue
            version = info.get("gameVersion", "")
            parts = version.split(".")
            patch = parts[0] + "." + parts[1] if len(parts) >= 2 else ""
            if patch != TARGET_PATCH:
                continue
            if info.get("gameDuration", 0) < 1200:
                continue
            try:
                timeline_data = get_data(timeline_url)
            except requests.HTTPError as error:
                if error.response.status_code == 404:
                    print("Timeline not found:", match_id)
                    continue
                raise
            frames = timeline_data["info"]["frames"]
            timestamps = []
            for frame in frames:
                timestamps.append(frame["timestamp"])
            valid = True
            for minute in [5, 10, 15]:
                target = minute * 60000
                if not timestamps:
                    valid = False
                    break
                closest = min(
                    abs(timestamp - target)
                    for timestamp in timestamps
                )
                if closest > 30000:
                    valid = False
                    break
            if not valid:
                print("Missing required frames:", match_id)
                continue
            with open(match_file, "w", encoding="utf-8") as file:
                json.dump(match_data, file, indent = 2)
            with open(timeline_file, "w", encoding="utf-8") as file:
                json.dump(timeline_data, file, indent=2)

            log_file = data_folder / "collection_sources.csv"
            new_log = not log_file.exists()
            with open(log_file, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if new_log:
                    writer.writerow([
                        "match_id",
                        "seed_tier",
                        "game_version",
                        "game_start"
                    ])
                writer.writerow([
                    match_id,
                    tier,
                    info.get("gameVersion", ""),
                    info.get("gameStartTimestamp", "")
                ])

            tier_downloaded += 1
            seed_downloaded += 1
            total_downloaded += 1

            print(
                "Saved:", match_id,
                "|", tier,
                "|", info.get("gameVersion", "")
            )
    print("New matches from", tier, "seeds:", tier_downloaded)
print()
print("=" * 50)
print("Collection finished.")
print("New matches downloaded:", total_downloaded)
print("=" * 50)
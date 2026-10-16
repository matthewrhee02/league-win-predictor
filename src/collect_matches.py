import json
from pathlib import Path
from urllib.parse import quote
from getpass import getpass
import requests

game_name = input("Enter your Riot game name: ")
tag_line = input("Enter your Riot tag line: ")
api_key = getpass("Enter your Riot API key: ")
headers = {
    "X-Riot-Token": api_key
}

account_url = (
    "https://americas.api.riotgames.com"
    f"/riot/account/v1/accounts/by-riot-id/{quote(game_name, safe='')}/{quote(tag_line, safe='')}"
)
response = requests.get(account_url, headers=headers, timeout=30)
response.raise_for_status()
account = response.json()
puuid = account["puuid"]
print("Successfully found your Riot account.")

matches_url = (
    "https://americas.api.riotgames.com"
    f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
)

params = {
    "queue": 420,
    "start": 0,
    "count": 5
}
response = requests.get(matches_url, headers=headers, params=params, timeout=30)
response.raise_for_status()

match_ids = response.json()
print("Found", len(match_ids), "ranked matches")

data_folder = Path("data/raw")
data_folder.mkdir(parents=True, exist_ok=True)

for match_id in match_ids:
    match_file = data_folder / f"{match_id}_match.json"
    timeline_file = data_folder / f"{match_id}_timeline.json"
    if match_file.exists() and timeline_file.exists():
        print("Already downloaded:", match_id)
        continue
    print("Downloading:", match_id)
    match_url = (
        "https://americas.api.riotgames.com"
        f"/lol/match/v5/matches/{match_id}"
    )
    timeline_url = (
        "https://americas.api.riotgames.com"
        f"/lol/match/v5/matches/{match_id}/timeline"
    )
    response = requests.get(match_url,headers=headers, timeout=30)
    response.raise_for_status()
    match_data = response.json()
    response = requests.get(timeline_url, headers=headers, timeout=30)
    response.raise_for_status()
    timeline_data = response.json()

    with open(match_file, "w", encoding="utf-8") as file:
        json.dump(match_data, file, indent=2)
    with open(timeline_file, "w", encoding="utf-8") as file:
        json.dump(timeline_data, file, indent=2)
    print("Saved:", match_id)

print("Finished downloading matches!")
import requests
import json
import time
from datetime import datetime
import os

CONFIG_PATH = "config.json"
LAST_VALID_CONFIG = {}


def load_config():
    global LAST_VALID_CONFIG
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

            # alapértelmezett értékek, ha hiányoznak
            config.setdefault("url1", "https://api.track.hunsail.hu/tabella")
            config.setdefault(
                "url2", "https://vihar.hunsail.hu:444/api/hunsail/getverseny/9786/gpstrack")
            config.setdefault("sleep", 10)
            config.setdefault("payload", {"start": 0, "limit": 10000})
            LAST_VALID_CONFIG = config
            return config
    except Exception as e:
        print(f"[Config hiba] {e} – utolsó ismert konfigurációval folytatom.")
        return LAST_VALID_CONFIG

headers = {
    "Content-Type": "application/json"
}

while True:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    config = load_config()

    try:
        # 1. Lekérjük az adatokat az első API-ból
        url = config["url1"]
        payload = config["payload"]

        res1 = requests.post(url, headers=headers, json=payload)
        if res1.status_code != 200:
            print("Hiba az első API lekérdezésénél:", res1.text)
            exit()

        data1 = res1.json().get("results", [])

        # 2. Második API
        res2 = requests.get(config["url2"])
        if res2.status_code != 200:
            print("Hiba a második API lekérdezésénél:", res2.text)
            exit()

        data2 = res2.json()
        track_list = data2.get("Nevezesek", [])

        # 3. Indexelés
        track_dict = {
            (item["Vitorlaszam"], item["HajoNev"], item["Kormanyos"]["Nev"]): item
            for item in track_list
        }

        # 4. Join
        joined_data = []
        for row in data1:
            sail_num = row.get("entity_sail_num")
            boat_name = row.get("entity_name")
            skipper_name = row.get("entity_helmsman")

            matching_row = track_dict.get((sail_num, boat_name, skipper_name))
            if matching_row:
                combined = {**row, **matching_row}
                joined_data.append(combined)

        # 5. Mentés
        with open("kekszalag_data.json", "w", encoding="utf-8") as f:
            json.dump(joined_data, f, ensure_ascii=False, indent=2)
            print(f"{timestamp} - [Siker] kekszalag_data.json fájlba a konfigurált lekérdezés eredménye kiírva!")

    except Exception as e:
        print(f"{timestamp} - [Kérés hiba] {e}")

    time.sleep(config["sleep"])
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
            config.setdefault("url", "https://api.regatta-test.ddc.sze.hu/tabella")
            config.setdefault("sleep", 5)
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
        response = requests.post(
            config["url"],
            headers=headers,
            json=config["payload"]
        )

        if response.status_code == 200:
            data = response.json()
            with open("kekszalag_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"{timestamp} - [Siker] kekszalag_data.json fájlba a konfigurált lekérdezés eredménye kiírva!")
        else:
            print(f"{timestamp} - [Hiba] HTTP {response.status_code} - {response.text}")

    except Exception as e:
        print(f"{timestamp} - [Kérés hiba] {e}")

    time.sleep(config["sleep"])
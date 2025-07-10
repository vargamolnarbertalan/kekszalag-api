import requests
import json
import time
from datetime import datetime
import os
from flask import Flask, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

CONFIG_PATH = "config.json"
DATA_FILE = "weather.json"
LAST_VALID_CONFIG = {}


def scrape_met():
    try:
        with sync_playwright() as p:
            data = []
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(config["url3"])
            page.wait_for_selector("body > table.tbl-def1")

            for x in range(15):
                place = page.query_selector(
                    f"body > table.tbl-def1 > tbody > tr:nth-child({x+1}) > th > a")
                windDir = page.query_selector(
                    f"body > table.tbl-def1 > tbody > tr:nth-child({x+1}) > td:nth-child(3)")
                windSpeed = page.query_selector(
                    f"body > table.tbl-def1 > tbody > tr:nth-child({x+1}) > td:nth-child(4)")
                beaufort = page.query_selector(
                    f"body > table.tbl-def1 > tbody > tr:nth-child({x+1}) > td:nth-child(5)")
                avgWindDir = page.query_selector(
                    f"body > table.tbl-def1 > tbody > tr:nth-child({x+1}) > td:nth-child(7)")
                avgWindSpeed = page.query_selector(
                    f"body > table.tbl-def1 > tbody > tr:nth-child({x+1}) > td:nth-child(8)")
                avgBeaufort = page.query_selector(
                    f"body > table.tbl-def1 > tbody > tr:nth-child({x+1}) > td:nth-child(9)")
                # print(place,windDir,windSpeed,beaufort,avgWindDir,avgWindSpeed,avgBeaufort)
                data.append({
                    "place": place.inner_text(),
                    "windDir": windDir.inner_text(),
                    "windSpeed": windSpeed.inner_text(),
                    "beaufort": beaufort.inner_text(),
                    "avgWindDir": avgWindDir.inner_text(),
                    "avgWindSpeed": avgWindSpeed.inner_text(),
                    "avgBeaufort": avgBeaufort.inner_text()
                })

            browser.close()

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        return False


def load_config():
    global LAST_VALID_CONFIG
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

            # alapértelmezett értékek, ha hiányoznak
            config.setdefault("url1", "https://api.track.hunsail.hu/tabella")
            config.setdefault(
                "url2", "https://vihar.hunsail.hu:444/api/hunsail/getverseny/9786/gpstrack")
            config.setdefault(
                "url3", "https://www.met.hu/idojaras/tavaink/balaton/mert_adatok/main.php")
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
    if scrape_met() == True:
        print(f"{timestamp} - Időjárás adatok frissítve.")
    else:
        print(f"{timestamp} - Hiba az időjárás adatok frissítése közben.")

    try:
        # 1. Lekérjük az adatokat az első API-ból
        url = config["url1"]
        payload = config["payload"]

        res1 = requests.post(url, headers=headers, json=payload)
        apiStatus = res1.status_code
        while apiStatus != 200:
            time.sleep(2)
            res1 = requests.post(url, headers=headers, json=payload)
            apiStatus = res1.status_code
            if apiStatus != 200:
                print("Hiba az első API lekérdezésénél:", res1.text)
            else:
                print("Első lekérdezés sikeres!")

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
            print(
                f"{timestamp} - [Siker] kekszalag_data.json fájlba a konfigurált lekérdezés eredménye kiírva!")
            
        # Filter out entries with null finish_time
        filtered = [item for item in joined_data if item["finish_time"]]

        # Build the output line
        line = ', '.join(
            f'{item["absolute_rank"]}. hely: {item["entity_name"]}' for item in filtered)

        # Write to a file
        with open("ticker.txt", "w", encoding="utf-8") as f:
            f.write(line)
            print(f"{timestamp} - Ticker frissítve.")

    except Exception as e:
        print(f"{timestamp} - [Kérés hiba] {e}")

    time.sleep(config["sleep"])
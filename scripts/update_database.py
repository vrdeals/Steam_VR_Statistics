"""The following external libraries must be installed: Requests, tqdm"""
import json
import datetime
import time
import sqlite3
import requests
from tqdm import tqdm
import sqlite_query


def get_vrgames_vrlfg():
    """Get the appid and name of all steam VR games with a VROnly tag and without a Overlay tag"""

    games = []
    url = "https://www.vrlfg.net/api/games"
    json_data = json.loads(requests.get(url).text)
    for item in json_data:
        if item["VROnly"] == 1 and item["Overlay"] == 0:
            games.append((item['gameid'], item["Name"]))
    return games


def get_vrgames_players(appid):
    """Get the number of players of a game for each day since release"""

    players = []
    url = f'https://steamdb.info/api/GetGraph/?type=concurrent_max&appid={appid}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/30.0.1599.101 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3"
    }
    json_data = json.loads(requests.get(url, headers=headers).text)
    success = json_data["success"]
    if success:
        time_stamp = int(json_data["data"]["start"])
        step = int(json_data["data"]["step"])
        players_list = json_data["data"]["values"]
        if players_list:
            for players_number in players_list:
                if players_number is not None and players_number > 0:
                    date = datetime.datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d')
                    players.append((appid, date, players_number))
                time_stamp += step
    elif "Please do not crawl" in json_data["error"]:
        time.sleep(120)   # The website prevents fast web crawling, therefore the waiting time.
        get_vrgames_players(appid)
    return players


def main():
    """
    Determines all Steam VR only games and the number of players.
    The required information is obtained from https://steamdb.info (number of daily players) and
    www.vrlfg.net (appid of all VR games) using the Requests and JSON library.
    The information is then stored in an SQLite database.
    """

    print("The database will be updated.")
    conn = sqlite3.connect('../database/vr_games_database.db')
    sqlite_query.create_database(conn)
    games = get_vrgames_vrlfg()
    print("The data is determined via web crawling which can take several minutes.")
    if games:
        player_numbers = []
        progressbar = tqdm(total=len(games))    # Displays a progress bar
        for game in games:
            appid = game[0]
            players = get_vrgames_players(appid)
            if players is not None and players:
                player_numbers.extend(players)
            progressbar.update(1)
            time.sleep(0.3)  # The website prevents fast web crawling, therefore the waiting time.
        progressbar.close()
        sqlite_query.reset(conn)
        sqlite_query.add_game(conn, games)
        sqlite_query.add_players(conn, player_numbers)
        print("The database was successfully updated.")
    conn.close()


if __name__ == "__main__":
    main()

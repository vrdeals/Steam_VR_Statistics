from lxml import html
import requests
import json
import datetime
import time
from tqdm import tqdm
import sqlite3
import sqlite_query


def get_vrgames_steam():
    """Get the appid and name of all steam VR games with a vr only tag, sorted by release date(desc)"""
    infinite_scrolling = 0
    counter = 0
    total_count = 0
    progressbar = 0
    games = []
    while True:
        url = 'https://store.steampowered.com/search/results/?query&start={}&count=50&dynamic_data=&sort_by=Released_' \
              'DESC&force_infinite=1&vrsupport=401&snr=1_7_7_230_7&infinite=1'.format(infinite_scrolling)
        json_data = json.loads(requests.get(url).text)
        if json_data["results_html"] != "\r\n<!-- List Items -->\r\n<!-- End List Items -->\r\n":
            if total_count == 0:
                total_count = json_data["total_count"]
                progressbar = tqdm(total=total_count)
                progressbar.set_description("Get VR Games")
            tree = html.fromstring(json_data["results_html"])
            appid_list = tree.xpath('//a/@data-ds-appid')
            game_list = tree.xpath('//span[@class="title"]/text()')
            for appid, game in zip(appid_list, game_list):
                counter += 1
                games.append((appid, game))
                progressbar.update(1)
                progressbar.refresh()
            infinite_scrolling += 50
        else:
            progressbar.refresh()
            progressbar.close()
            print(url)
            return games


def get_vrgames_vrlfg():
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
    url = 'https://steamdb.info/api/GetGraph/?type=concurrent_max&appid={}'.format(appid)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'}
    try:
        json_data = json.loads(requests.get(url, headers=headers).text)
        success = json_data["success"]
        if success:
            time_stamp = int(json_data["data"]["start"])
            step = int(json_data["data"]["step"])
            players_list = json_data["data"]["values"]
            if players_list:
                for players_number in players_list:
                    if players_number is not None:
                        date = datetime.datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d')
                        players.append((appid, date, players_number))
                    time_stamp += step
        if not players:
            players = ""
        return players
    except ValueError:
        """The website prevents web crawling, so the program waits 2 seconds before retrieving further data."""
        time.sleep(2)
        get_vrgames_players(appid)


# def update_required(conn):
#     """checks if more than 1 month has passed since the last update"""
#     update = False
#     today = datetime.date.today()
#     today = int(today.strftime('%m'))
#     last_update = sqlite_query.last_update(conn)[0]
#     if last_update is None:
#         update = True
#     else:
#         last = int(last_update.split("-")[1])
#         delta = today - last
#         if delta > 1:
#             update = True
#     return update


def main():
    print("The database will be updated.")
    conn = sqlite3.connect('vr_games_database.db')
    sqlite_query.create_database(conn)
    games = get_vrgames_vrlfg()
    print("The data is determined via web crawling which can take several minutes.")
    if games:
        player_numbers = []
        progressbar = tqdm(total=len(games))
        for game in games:
            appid = game[0]
            players = get_vrgames_players(appid)
            if players is not None:
                player_numbers.extend(players)
            progressbar.update(1)
        progressbar.close()
        sqlite_query.reset(conn)
        sqlite_query.add_game(conn, games)
        sqlite_query.add_players(conn, player_numbers)
    conn.close()


if __name__ == "__main__":
    main()

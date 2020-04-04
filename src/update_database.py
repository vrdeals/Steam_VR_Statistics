"""Requires Python 3.8 or higher and the external libraries Requests, lxml and tqdm."""
import json
from datetime import datetime, date, timedelta
import time
from lxml import html
import requests
from tqdm import tqdm
import sql_query as sql


def check_appids_existing(appid_list, game_list):
    """Checks if the appid does not yet exist in the database"""
    games = []
    for appid, game in zip(appid_list, game_list):
        existing_appid = sql.get_appid(appid)
        if existing_appid is None:
            print("Appid:", appid, "Game:", game)
            games.append((appid, game))
    return games


def get_new_vrgames_steam():
    """Returns the appid and name of new steam VR only games, sorted by release date(desc)"""
    infinite_scrolling = 0
    new_games = []
    while True:
        url = f'https://store.steampowered.com/search/results/?query&start={infinite_scrolling}' \
              f'&count=50&dynamic_data=&sort_by=Released_DESC&force_infinite=1' \
              f'&category1=998&vrsupport=401&snr=1_7_7_230_7&infinite=1'
        json_data = json.loads(requests.get(url).text)
        if json_data["results_html"] == "\r\n<!-- List Items -->\r\n<!-- End List Items -->\r\n":
            break
        tree = html.fromstring(json_data["results_html"])
        appid_list = tree.xpath('//a/@data-ds-appid')
        game_list = tree.xpath('//span[@class="title"]/text()')
        if games := check_appids_existing(appid_list, game_list):
            new_games.extend(games)
        else:
            break
        infinite_scrolling += 50
    return new_games


def get_vrgames_players(appid):
    """Get the number of players of a game for each day since release."""
    players = []
    players_list = []
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
        players_list = json_data["data"]["values"]
    elif "Please do not crawl" in json_data["error"]:
        tqdm.write("\nThe program is waiting 400 seconds because the website prevents web crawling")
        time.sleep(400)   # The website prevents fast web crawling, therefore the waiting time.
        get_vrgames_players(appid)
    if players_list:
        time_stamp = int(json_data["data"]["start"])
        step = int(json_data["data"]["step"])
        for players_number in players_list:
            if players_number is not None and players_number > 0:
                date_daily_peak = datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d')
                players.append((appid, date_daily_peak, players_number))
            time_stamp += step
    return players


def number_of_players(games):
    """Shows a progress bar and returns a list with the number of players of each VR game"""
    player_numbers = []
    if not games:
        return player_numbers
    print("The data is determined via web crawling which can take a long time.")
    progressbar = tqdm(total=len(games))  # Displays a progress bar
    for game in games:
        appid = game[0]
        players = get_vrgames_players(appid)
        if players is not None and players:
            player_numbers.extend(players)
        progressbar.update(1)
        time.sleep(0.3)  # website prevents fast web crawling, therefore the waiting time
    progressbar.close()
    return player_numbers


def update_required():
    """Checks if the last update is older than the last day of the previous month."""
    update = False
    today = date.today()
    first_day_this_month = date(today.year, today.month, 1)
    last_day_of_the_previous_month = first_day_this_month - timedelta(1)
    last_day_of_the_previous_month = last_day_of_the_previous_month.strftime("%Y-%m-%d")
    sql.create_database()
    last_update = sql.last_update()
    if last_update is None:
        update = True
    elif last_update < last_day_of_the_previous_month:
        update = True
    if update:
        print("The database will be updated.")
    return update


def main():
    """
    Determines all Steam VR only games and the number of players.
    The required information is obtained from https://store.steampowered.com (appid of all VR games)
    and https://steamdb.info (number of daily players) using the Requests, JSON and lxml library.
    The information is then stored in an SQLite database.
    """
    print("Checking if new VR games are available.")
    games = get_new_vrgames_steam()
    sql.add_game(games)
    if update := update_required():
        games = sql.get_all_games()
    elif not games:
        print("The database is up-to-date, no update is required.")
    numbers = number_of_players(games)
    if update:
        sql.reset()
    sql.add_players(numbers)
    sql.close_database()


if __name__ == "__main__":
    main()

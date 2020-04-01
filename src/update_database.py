"""The external libraries Requests and tqdm must be installed."""
import json
from datetime import datetime, date, timedelta
import time
import requests
from tqdm import tqdm
import sql_query as sql


def get_vrgames_vrlfg():
    """Get the appid and name of all steam VR games with a VROnly tag and without a Overlay tag."""
    games = []
    url = "https://www.vrlfg.net/api/games"
    json_data = json.loads(requests.get(url).text)
    for item in json_data:
        if item["VROnly"] == 1 and item["Overlay"] == 0:
            games.append((item['gameid'], item["Name"]))
    return games


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
    return update


def update_database(games, numbers):
    """adds the games and player numbers to the database"""
    sql.reset()
    sql.add_game(games)
    sql.add_players(numbers)


def main():
    """
    Determines all Steam VR only games and the number of players.
    The required information is obtained from https://steamdb.info (number of daily players) and
    www.vrlfg.net (appid of all VR games) using the Requests and JSON library.
    The information is then stored in an SQLite database.
    """
    if update_required():
        print("The database will be updated.")
        games = get_vrgames_vrlfg()
        print("The data is determined via web crawling which can take a long time.")
        numbers = number_of_players(games)
        update_database(games, numbers)
        print("The database was successfully updated.")
    else:
        print("The database is up-to-date, no update is required.")
    sql.close_database()


if __name__ == "__main__":
    main()

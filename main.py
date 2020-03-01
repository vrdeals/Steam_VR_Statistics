from lxml import html
import requests
import json
import datetime
from time import strptime
import database
import stastitics
import sqlite3


class Game:
    def __init__(self, appid, title, players=""):
        self.appid = appid
        self.title = title
        self.players = players

    def number_of_players(self):
        self.players = get_vrgames_players(self.appid)

    def print_game(self):
        print(self.appid, self.title, self.players)

    def add_game_to_database(self, c):
        database.add_game(c, (self.appid, self.title))
        for item in self.players:
            date = item[0]
            players = item[1]
            peak = item[2]
            database.add_players(c, (self.appid, date, players, peak))


def get_vrgames_steam():
    """Get the appid and name of all steam VR games with a vr only tag, sorted by release date(desc)"""
    infinite_scrolling = 0
    counter = 0
    games = []
    while True:
        url = 'https://store.steampowered.com/search/results/?query&start={}&count=50&dynamic_data=&sort_by=Released_' \
              'DESC&force_infinite=1&vrsupport=401&snr=1_7_7_230_7&infinite=1'.format(infinite_scrolling)
        json_data = json.loads(requests.get(url).text)
        if json_data["results_html"] != "\r\n<!-- List Items -->\r\n<!-- End List Items -->\r\n":
            tree = html.fromstring(json_data["results_html"])
            appid_list = tree.xpath('//a/@data-ds-appid')
            game_list = tree.xpath('//span[@class="title"]/text()')
            for appid, game in zip(appid_list, game_list):
                counter += 1
                print(counter, appid, game)
                games.append(Game(appid, game))
            infinite_scrolling += 50
        else:
            return games


def get_vrgames_players(appid):
    """Get the number of players of a game for each month since release"""
    players = []
    url = 'https://steamcharts.com/app/{}'.format(appid)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    date_list = tree.xpath('//td[@class="month-cell left"]/text()')
    players_list = tree.xpath('//td[@class="right num-f"]/text()')
    players_peak_list = tree.xpath('//td[@class="right num"]/text()')
    if players_list:
        for date, avg_players, peak_players in zip(date_list, players_list, players_peak_list):
            date = date.strip().split(" ")
            month = '%0.2d' % strptime(date[0], '%B').tm_mon
            year = date[1]
            date = "{}-{}".format(year, month)
            players.append([date, avg_players, peak_players])
    if not players:
        players = ""
    return players


def update_required(c):
    """checks if more than 1 month has passed since the last update"""
    update = False
    today = datetime.date.today()
    today = int(today.strftime('%m'))
    last_update = database.last_update(c)[0]
    if last_update is None:
        update = True
    else:
        last = int(last_update.split("-")[1])
        delta = today - last
        if delta > 1:
            update = True
    return update


def main():
    database_location = 'vr_games_database.db'
    conn = sqlite3.connect(database_location)
    c = conn.cursor()
    database.create_database(c)
    if update_required(c):
        print("The database will be updated.")
        games = get_vrgames_steam()
        for game in games:
            game.number_of_players()
            game.print_game()
        database.reset(c)
        for game in games:
            game.add_game_to_database(c)
    print("The database is up to date. "
          "All VR only games and the number of players until the end of last month are included in the statistics.")
    stastitics.charts(c)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()

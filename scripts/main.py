#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import html
import requests
import json
import datetime
from time import strptime
from scripts import database
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
            database.add_players(c, (self.appid, date, players))


def get_vrgames_steam(c):  # Get the appid and name of all steam VR games, sorted by release date(desc) and vr only tag
    infinite_scrolling = 0
    counter = 0
    games = []
    while True:
        url = 'https://store.steampowered.com/search/results/?query&start=' + str(infinite_scrolling) + \
                '&count=100&dynamic_data=&sort_by=Released_DESC&force_infinite=1&vrsupport=401&snr=1_7_7_230_7&' \
                'infinite=1'
        json_data = json.loads(requests.get(url).text)
        if json_data["results_html"] != "\r\n<!-- List Items -->\r\n<!-- End List Items -->\r\n":
            tree = html.fromstring(json_data["results_html"])
            appid_list = tree.xpath('//a/@data-ds-appid')
            game_list = tree.xpath('//span[@class="title"]/text()')
            for appid, game in zip(appid_list, game_list):
                counter += 1
                if database.check_game(c, (appid,)) is None:
                    print(counter, appid, game)
                    games.append(Game(appid, game))
                else:
                    print(counter, appid, game, "already in the database")
            infinite_scrolling += 100
        else:
            return games


def get_vrgames_players(appid):  # Get the number of players of a game for each month since release
    players = []
    url = 'https://steamcharts.com/app/' + appid
    page = requests.get(url)
    tree = html.fromstring(page.content)
    date_list = tree.xpath('//td[@class="month-cell left"]/text()')
    players_list = tree.xpath('//td[@class="right num-f"]/text()')
    last_30_days = tree.xpath('//td[@class="right num-f italic"]/text()')
    now = datetime.date.today()
    if last_30_days:
        players.append([now.strftime('%Y-%m'), last_30_days[0]])
    if players_list:
        for date, avg_players in zip(date_list, players_list):
            date = date.strip().split(" ")
            month = '%0.2d' % strptime(date[0], '%B').tm_mon
            year = date[1]
            date = "{}-{}".format(year, month)
            players.append([date, avg_players])
    if not players:
        players = ""
    return players


def main():
    database_location = '../database/vr_games.db'
    conn = sqlite3.connect(database_location)
    c = conn.cursor()
    database.create_database(c)
    games = get_vrgames_steam(c)
    for game in games:
        game.number_of_players()
        game.print_game()
        game.add_game_to_database(c)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()

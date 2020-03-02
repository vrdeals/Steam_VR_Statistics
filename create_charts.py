import matplotlib.pyplot as plt
from dateutil import parser
from matplotlib import style
import sqlite3
import sqlite_query


def graph_data(data, title):
    dates = []
    values = []
    for item in data:
        dates.append(parser.parse(item[0]))
        values.append(item[1])
    # plt.plot(dates, values, "-b", label="average number of players")
    plt.figure(1)
    plt.plot_date(dates, values, '-')
    plt.title(title)
    # plt.legend(loc="upper left")
    plt.grid(True)


def main():
    conn = sqlite3.connect('vr_games_database.db')
    sqlite_query.create_database(conn)
    style.use('seaborn-dark')
    data = sqlite_query.peak_players_online(conn)
    graph_data(data, "Peak number of players on Steam (VR games only)")
    plt.show()


if __name__ == "__main__":
    main()

import matplotlib.pyplot as plt
from dateutil import parser
from matplotlib import style
import numpy as np
import sqlite3
import sqlite_query


def graph_data(data):
    dates = []
    values = []
    for item in data:
        dates.append(parser.parse(item[0]))
        values.append(item[1])
    # plt.plot(dates, values, "-b", label="average number of players")
    plt.plot_date(dates, values, '-')
    plt.title("Peak number of players on Steam (VR games only)")
    # plt.legend(loc="upper left")
    plt.grid(True)


def bar_diagram(data):
    top10games = []
    top10players =[]
    style.use('seaborn-dark')
    fig, ax = plt.subplots()
    for item in data:
        print(item[0])
        top10games.append(item[0])
        top10players.append(item[1])
    y_pos = np.arange(len(top10games))
    ax.barh(y_pos, top10players, align='center', ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top10games)
    ax.invert_yaxis()  # labels von oben nach unten
    # ax.set_xlabel('')
    ax.set_title('Top 10 maximum number of simultaneous players on steam')
    plt.grid(True)


def main():
    conn = sqlite3.connect('vr_games_database.db')
    sqlite_query.create_database(conn)
    style.use('seaborn-dark')
    data = sqlite_query.peak_players_online(conn)
    plt.figure(1)
    graph_data(data)
    data = sqlite_query.top10(conn)
    print(data)
    bar_diagram(data)
    # top5 = [620980, 555160, 823500, 629730, 471710]
    # plt.figure(2)
    # for item in top5:
    #     data = sqlite_query.peak_players_appid(conn, item)
    #     graph_data(data, "TupPeak number of players on Steam (VR games only)")
    plt.show()


if __name__ == "__main__":
    main()

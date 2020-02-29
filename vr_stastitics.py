import sqlite3
import matplotlib.pyplot as plt
from dateutil import parser
# from matplotlib import style
import database


def graph_data(data):
    dates = []
    values = []
    for row in data:
        dates.append(parser.parse(row[0]))
        values.append(row[1])
    # plt.plot(dates, values, "-b", label="average number of players")
    plt.plot_date(dates, values, '-')
    plt.title("Average number of players on Steam(VR games only)",
              fontdict={'family': 'serif',
                        'color': 'black',
                        'weight': 'bold',
                        'size': 12})
    # plt.legend(loc="upper left")
    plt.show()


def main():
    # style.use('fivethirtyeight')
    database_location = 'vr_games_database.db'
    conn = sqlite3.connect(database_location)
    c = conn.cursor()
    data = database.avg_players(c)
    graph_data(data)


if __name__ == "__main__":
    main()

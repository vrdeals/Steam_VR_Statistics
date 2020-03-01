import matplotlib.pyplot as plt
from dateutil import parser
from matplotlib import style
import database


def graph_data(data, title):
    dates = []
    values = []
    for row in data:
        dates.append(parser.parse(row[0]))
        values.append(row[1])
    # plt.plot(dates, values, "-b", label="average number of players")
    plt.plot_date(dates, values, '-')
    plt.title(title,
              # fontdict={'family': 'arial',
              #           'color': 'black',
              #           'weight': 'bold',
              #           'size': 12}
              )
    # plt.legend(loc="upper left")
    plt.grid(True)
    plt.show()


def charts(c):
    style.use('seaborn-dark')
    data = database.avg_players(c)
    graph_data(data, "Average number of players on Steam(VR games only)")
    # graph_data(data, "Peak number of players on Steam(VR games only)")


import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from dateutil import parser
from matplotlib import style
import matplotlib.pylab as pylab
import seaborn as sns
import pandas as pd
import sqlite3
from scripts import sqlite_query


def top10_2020(conn):
    """Creates a chart of the 10 most used VR games since 2020"""
    games = sqlite_query.top10(conn)
    games = change_game_title(games)

    sns.set_style("whitegrid")
    sns.set(font_scale=0.7)

    # Initialize the matplotlib figure
    f, ax = plt.subplots()
    ax.xaxis.set_major_locator(MultipleLocator(250))

    # Creates a Panda data frame with the data from the sqlite database
    top10 = pd.DataFrame(games, columns=['game', 'max_players', 'avg_players'])

    # Plot the maximum number of players
    sns.set_color_codes("pastel")
    sns.barplot(x="max_players", y="game", data=top10, label="The maximum number of players (highest peak)", color="b")

    # Plot the average number of players
    sns.set_color_codes("muted")
    fig = sns.barplot(x="avg_players", y="game", data=top10,
                      label="The average number of daily players", color="b")
    fig.axes.set_title("The most played Steam VR games since 2020", fontsize=10)
    fig.set_xlabel("")
    fig.set_ylabel("")

    # Add a legend and informative axis label
    ax.legend(ncol=2, loc="lower right", frameon=False)
    sns.despine(left=True, bottom=True)

    # save the plot and cuts off the edges
    plt.savefig('../images/vrgames_top10_2020.png', bbox_inches='tight')


def peak_players_online(conn):
    """Creates a chart of the 10 most used VR games since 2020"""
    data = sqlite_query.peak_players_online(conn)
    dates = []
    values = []
    for item in data:
        dates.append(parser.parse(item[0]))
        values.append(item[1])
    style.use('seaborn-dark')
    plt.plot_date(dates, values, '-')
    plt.title("Progress of VR usage based on the monthly average of the daily peak values of all Steam VR only games.")
    plt.grid(True)
    plt.savefig('../images/vrgames_avg_peak_over_time.png', bbox_inches='tight')


def change_game_title(games):
    """Changes game title that are too long to be displayed in the chart"""
    titles = ["Skyrim VR", "The Walking Dead", "Hot Dogs"]
    games_list = []
    for game in games:
        match = False
        for title in titles:
            if title in game[0]:
                games_list.append((title, game[1], game[2]))
                match = True
        if not match:
            games_list.append((game[0], game[1], game[2]))
    return games_list


def main():

    # database connect
    conn = sqlite3.connect('../database/vr_games_database.db')

    #  Defines the basic layot for all charts
    plt.rcParams['axes.xmargin'] = 0.01
    plt.rcParams['axes.ymargin'] = 0.01
    params = {'legend.fontsize': 'small',
              'figure.figsize': (9, 5),
              'axes.labelsize': 'small',
              'axes.titlesize': 'medium',
              'xtick.labelsize': 'small',
              'ytick.labelsize': 'small'}
    pylab.rcParams.update(params)

    peak_players_online(conn)
    top10_2020(conn)

    plt.show()  # Displays the charts
    print("The images were successfully saved in the images folder.")


if __name__ == "__main__":
    main()

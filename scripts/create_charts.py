"""The following external libraries must be installed: matplotlib, seaborn, pandas"""
import sqlite3
from dateutil import parser
from matplotlib import pyplot as plt, style, pylab as pylab
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import pandas as pd


def top10_sql():
    """Returns the 10 most played VR games since 2020 as a list"""
    c.execute('''
    SELECT title, max(players) as Maxplayers, round(avg(players)) as Average from vr_players
    INNER JOIN vr_games ON vr_games.appid = vr_players.appid
    WHERE date >= '2020-01'
    Group by vr_players.appid
    Order by Maxplayers DESC
    Limit 10
    ''')
    return c.fetchall()


def peak_players_online_sql():
    """Returns the monthly average of the daily peak values since 2016-03 as a list"""
    c.execute('''
    Select new_date, sum(average) from (SELECT strftime('%Y-%m', date) as new_date, 
    sum(players)/(julianday(date,'start of month','+1 month') - julianday(date,'start of month')) 
    as average from vr_players
    WHERE date != '2019-07-24' and date > '2016-03' and date < date('now','start of month')
    Group by appid, new_date
    Order by new_date)
    where average >= 1
    Group by new_date
    ''')
    return c.fetchall()


def top10_2020():
    """Creates a chart of the 10 most used VR games since 2020 with the seaborn library"""

    # Fetches the data from the sqlite database
    games = top10_sql()

    # changes the title length
    games = change_game_title(games)

    # Defines the used graphic style and reduces the text size to fit all information on the chart
    sns.set_style("whitegrid")
    sns.set(font_scale=0.7)

    # Initialize the matplotlib figure
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(MultipleLocator(250))

    # Creates a Panda data frame with the data from the sqlite database
    top10 = pd.DataFrame(games, columns=['game', 'max_players', 'avg_players'])

    # Plot the maximum number of players
    sns.set_color_codes("pastel")
    sns.barplot(x="max_players", y="game", data=top10,
                label="The maximum peak value achieved since 2020", color="b")

    # Plot the average number of players
    sns.set_color_codes("muted")
    fig = sns.barplot(x="avg_players", y="game", data=top10,
                      label="The average daily peak since 2020", color="b")
    fig.axes.set_title("The most played Steam VR games since 2020", fontsize=10)
    fig.set_xlabel("")
    fig.set_ylabel("")

    # Add a legend and informative axis label
    ax.legend(ncol=2, loc="lower right", frameon=False)
    sns.despine(left=True, bottom=True)

    # save the plot and cuts off the edges
    plt.savefig('../images/vrgames_top10_2020.png', bbox_inches='tight')


def peak_players_online():
    """Creates a chart which shows the use of VR since 2016 with the matplotlib library"""

    data = peak_players_online_sql()
    dates = []
    players = []
    for item in data:
        dates.append(parser.parse(item[0]))     # formatting string into date
        players.append(item[1])
    style.use('seaborn-dark')
    plt.plot_date(dates, players, '-')
    plt.title("Progress of VR usage based on the monthly average of the daily peak values "
              "of all Steam VR only games.")
    plt.grid(True)
    plt.savefig('../images/vrgames_avg_peak_over_time.png', bbox_inches='tight')


def change_game_title(games):
    """Changes game title that are too long to be displayed in the chart"""

    shortened_title_names = ["Skyrim VR", "The Walking Dead", "Hot Dogs"]
    games_list = []
    for game in games:
        game_title, max_players, avg_players = game
        for short_title in shortened_title_names:
            if short_title in game_title:
                games_list.append((short_title, max_players, avg_players))
                break
        else:
            games_list.append((game_title, max_players, avg_players))
    return games_list


def main():
    """Generates Charts with the Matplotlib and Seaborn libraries"""
    print("The charts will be created which can take a few seconds.")

    #  Defines the basic layout for all charts
    plt.rcParams['axes.xmargin'] = 0.01
    plt.rcParams['axes.ymargin'] = 0.01
    params = {'legend.fontsize': 'small',
              'figure.figsize': (9, 5),
              'axes.labelsize': 'small',
              'axes.titlesize': 'medium',
              'xtick.labelsize': 'small',
              'ytick.labelsize': 'small'}
    pylab.rcParams.update(params)

    peak_players_online()
    top10_2020()
    conn.close()

    # Displays the charts
    plt.show()
    print("The charts were successfully saved in the images folder.")


if __name__ == "__main__":
    conn = sqlite3.connect('../database/vr_games_database.db')
    c = conn.cursor()
    main()

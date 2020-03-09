"""The following external libraries must be installed: matplotlib, seaborn, pandas"""
import sqlite3
from dateutil import parser
from matplotlib import pyplot as plt, style, pylab as pylab
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import pandas as pd

# Database connection
conn = sqlite3.connect('../database/vr_games_database.db')
c = conn.cursor()


def top10_sql():
    """Returns the 10 most played VR games since 2020 as a list"""
    c.execute('''
    SELECT vr_players.appid, title, max(players) as Maxplayers, round(avg(players)) as Average from vr_players
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


def max_peak_players_appid(appid):
    """Returns the monthly max peak values of a game as a list"""
    c.execute(f'''
    SELECT strftime('%Y-%m', date) as new_date, 
    max(players) as average from vr_players
    WHERE appid ="{appid}"  and date >= '2019' and date != '2019-07-24' and date < date('now','start of month')
    Group by new_date
    ''')
    return c.fetchall()


def top10_chart(sql_data):
    """Creates a chart of the 10 most used VR games since 2020 with the seaborn library"""
    # changes the title length
    sql_data = change_game_title(sql_data)

    # Defines the used graphic style and reduces the text size to fit all information on the chart
    sns.set_style("whitegrid")
    sns.set(font_scale=0.7)

    # Initialize the matplotlib figure
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(MultipleLocator(250))

    # Creates a Panda data frame with the data from the sqlite database
    top10 = pd.DataFrame(sql_data, columns=['appid', 'game', 'max_players', 'avg_players'])

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


def peak_players_chart(sql_data, chart_title, legend=""):
    """Creates a chart which shows the peak values with the matplotlib library"""
    dates_list = []
    players_list = []
    for date, players in sql_data:
        dates_list.append(parser.parse(date))     # formatting string into date
        players_list.append(players)
    plt.title(chart_title)
    if legend:
        plt.plot(dates_list, players_list, label=legend)
        plt.legend(loc="upper left")
    else:
        plt.plot(dates_list, players_list)
    plt.grid(True)


def change_game_title(sql_data):
    """Changes game title that are too long to be displayed in the chart"""
    shortened_title_names = ["Skyrim VR", "The Walking Dead", "Hot Dogs"]
    games_list = []
    for appid, game_title, max_players, avg_players in sql_data:
        for short_title in shortened_title_names:
            if short_title in game_title:
                games_list.append((appid, short_title, max_players, avg_players))
                break
        else:
            games_list.append((appid, game_title, max_players, avg_players))
    return games_list


def main():
    """Generates Charts with the Matplotlib and Seaborn libraries"""
    print("The charts will be created which can take a few seconds.")

    #  Defines the basic layout for all charts
    style.use('seaborn')
    plt.rcParams['axes.xmargin'] = 0.01
    plt.rcParams['axes.ymargin'] = 0.01
    params = {'legend.fontsize': 'small',
              'figure.figsize': (8, 5),
              'axes.labelsize': 'small',
              'axes.titlesize': 'medium',
              'xtick.labelsize': 'small',
              'ytick.labelsize': 'small'}
    pylab.rcParams.update(params)

    # Creates the charts with the data from the sql queries and saves them

    chart_title = "Steam VR usage of all VR games based on the monthly average of the daily peak values"
    peak_players_chart(peak_players_online_sql(), chart_title)
    plt.savefig('../images/avg_peak_over_time.png', bbox_inches='tight')

    plt.subplots()
    chart_title = "The maximum number of simultaneous players on Steam VR"
    top10sql = top10_sql()
    for appid, name, *_ in top10sql[:6]:
        peak_players_chart(max_peak_players_appid(appid), chart_title, name)
    plt.savefig('../images/max_peak.png', bbox_inches='tight')

    top10_chart(top10sql)
    plt.savefig('../images/top10_2020.png', bbox_inches='tight')
    conn.close()

    # Displays the charts
    plt.show()
    print("The charts were successfully saved in the images folder.")


if __name__ == "__main__":
    main()

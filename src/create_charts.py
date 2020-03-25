"""The external libraries matplotlib, seaborn and pandas must be installed."""
import sqlite3
from datetime import date, timedelta
from dateutil import parser
from matplotlib import pyplot as plt, style, pylab as pylab
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import pandas as pd

# Database connection
conn = sqlite3.connect('../database/vr_games_database.db')
c = conn.cursor()


def sql_top10():
    """Returns the 10 most played VR games since 2016-03 as a list."""
    c.execute('''
    SELECT vr_players.appid, title, max(players) as Maxplayers, round(avg(players)) as Average from vr_players
    INNER JOIN vr_games ON vr_games.appid = vr_players.appid
    WHERE vr_players.appid != 450110 and vr_players.appid != 692530 and date != '2019-07-24' and date > '2016-03'
    GROUP by vr_players.appid
    ORDER by Maxplayers DESC
    Limit 10
    ''')
    return c.fetchall()


def sql_top10_previous_month(start_date):
    """Returns the 10 most played VR games from given date to end of last month as a list."""
    c.execute(f'''
    SELECT vr_players.appid, title, max(players) as Maxplayers, round(avg(players)) as Average from vr_players
    INNER JOIN vr_games ON vr_games.appid = vr_players.appid
    WHERE date >= '{start_date}' and date < date('now','start of month')
    GROUP by vr_players.appid
    ORDER by Maxplayers DESC
    Limit 10
    ''')
    return c.fetchall()


def sql_peak_players():
    """Returns the monthly average of the daily peak values since 2016-03 as a list."""
    c.execute('''
    Select new_date, sum(average) from (SELECT strftime('%Y-%m', date) as new_date, 
    sum(players)/(julianday(date,'start of month','+1 month') - julianday(date,'start of month')) 
    as average from vr_players
    WHERE date != '2019-07-24' and date > '2016-03' and date < date('now','start of month')
    GROUP by appid, new_date
    ORDER by new_date)
    WHERE average >= 1
    Group by new_date
    ''')
    return c.fetchall()


def sql_max_peak_players(appid):
    """Returns the monthly max peak values of a game as a list."""
    c.execute(f'''
    SELECT strftime('%Y-%m', date) as new_date, 
    max(players) as average from vr_players
    WHERE appid ='{appid}'  and date >= '2019' and date != '2019-07-24' and date < date('now','start of month')
    GROUP by new_date
    ''')
    return c.fetchall()


def sql_max_peak_players_monthly(month):
    """Returns the monthly peak values (sum) of all games as a list."""
    c.execute(f'''
    SELECT strftime('%d', date), sum(players) from (
    SELECT date, players from vr_players
    WHERE date like '{month}%')
    GROUP by date
    ''')
    # print(c.fetchall())
    return c.fetchall()


def top10_chart(sql_data, chart_title, month=""):
    """Creates a chart of the 10 most used VR games since 2020 with the seaborn library."""
    # changes the title length
    sql_data = change_game_title(sql_data)

    # Defines the used graphic style and reduces the text size to fit all information on the chart
    sns.set_style("whitegrid")
    sns.set(font_scale=0.7)

    # Initialize the matplotlib figure
    fig, ax = plt.subplots()

    # Creates a Panda data frame with the data from the sqlite database
    top10 = pd.DataFrame(sql_data, columns=['appid', 'game', 'max_players', 'avg_players'])

    # Plot the maximum number of players
    sns.set_color_codes("pastel")
    multiple_locator = 2500
    if month:
        month = f' in {month}'
        multiple_locator = 250
    else:
        sns.set_color_codes("muted")
    ax.xaxis.set_major_locator(MultipleLocator(multiple_locator))
    fig = sns.barplot(x="max_players", y="game", data=top10,
                      label=f"The maximum number of concurrent users{month}", color="b")
    fig.axes.set_title(f'{chart_title}', fontsize=10)
    fig.set_xlabel("")
    fig.set_ylabel("")

    # Plot the average number of players
    if month:
        sns.set_color_codes("muted")
        fig = sns.barplot(x="avg_players", y="game", data=top10, label=f"The average daily peak{month}", color="b")
        fig.set_xlabel("")
        fig.set_ylabel("")

    # Add a legend and informative axis label
    ax.legend(ncol=2, loc="lower right", frameon=False)
    sns.despine(left=True, bottom=True)


def peak_players_chart(sql_data, chart_title, legend="", location="upper left"):
    """Creates a chart which shows the peak values with the matplotlib library."""
    dates_list = []
    players_list = []
    for date_data, players in sql_data:
        if len(date_data) > 2:
            date_data = parser.parse(date_data)  # formatting string into date
        dates_list.append(date_data)
        players_list.append(players)
    plt.title(chart_title)
    if legend:
        plt.plot(dates_list, players_list, label=legend)
        plt.legend(loc=location)
    else:
        plt.plot(dates_list, players_list)
    plt.grid(True)


def change_game_title(sql_data):
    """Changes game title that are too long to be displayed in the chart"""
    shortened_title_names = ["Skyrim VR", "The Walking Dead", "Hot Dogs", "Rick and Morty"]
    games_list = []
    for appid, game_title, max_players, avg_players in sql_data:
        for short_title in shortened_title_names:
            if short_title in game_title:
                games_list.append((appid, short_title, max_players, avg_players))
                break
        else:
            games_list.append((appid, game_title, max_players, avg_players))
    return games_list


def first_day_previous_month():
    """Returns the date of the first day of the previous month"""
    today = date.today()
    first_day_this_month = date(today.year, today.month, 1)
    last_day_of_the_previous_month = first_day_this_month - timedelta(1)
    first_day_of_the_previous_month = date(
        last_day_of_the_previous_month.year,
        last_day_of_the_previous_month.month, 1)
    return first_day_of_the_previous_month


def main():
    """Generates Charts with the Matplotlib and Seaborn libraries."""
    print("The charts will be created which can take a few seconds.")

    #  Defines the basic layout for all charts
    style.use('seaborn')
    plt.rcParams['axes.xmargin'] = 0.01
    plt.rcParams['axes.ymargin'] = 0.01
    params = {'legend.fontsize': 'small',
              'figure.figsize': (8.5, 5),
              'axes.labelsize': 'small',
              'axes.titlesize': 'medium',
              'xtick.labelsize': 'small',
              'ytick.labelsize': 'small'}
    pylab.rcParams.update(params)

    # Creates the charts with the data from the sql queries and saves them
    chart_title = "Steam VR usage of all VR games based on the monthly average" \
                  " of the daily peak values"
    sql = sql_peak_players()
    peak_players_chart(sql, chart_title)
    plt.savefig('../images/avg_peak_over_time.png')

    plt.subplots()
    chart_title = "The number of concurrent users on Steam VR for some games"
    first_day = first_day_previous_month()
    sql = sql_top10_previous_month(first_day)
    for appid, name, *_ in sql[:6]:
        peak_players_chart(sql_max_peak_players(appid), chart_title, name)
    plt.savefig('../images/max_peak.png')

    previous_month = first_day.strftime("%B %Y")
    chart_title = f"The most played Steam VR games in {previous_month}"
    top10_chart(sql, chart_title, first_day.strftime("%B"))
    plt.savefig('../images/top10.png')
    plt.savefig(f'../images/top10_{first_day.strftime("%Y_%m")}.png')

    plt.subplots()
    chart_title = "VR usage of the last 2 months based on " \
                  "the sum of the daily peak values of all Steam VR only games"
    months = ("2020-01", "2020-02")
    for month in months:
        sql = sql_max_peak_players_monthly(month)
        peak_players_chart(sql, chart_title, month, location='upper right')
    plt.savefig('../images/monthly_vrusage.png')

    sql = sql_top10()
    chart_title = "Steam VR games with the highest number of concurrent users since 2016"
    top10_chart(sql, chart_title)
    plt.savefig('../images/top10_max_peak.png')

    conn.close()

    # Displays the charts
    plt.show()
    print("The charts were successfully saved in the images folder.")


if __name__ == "__main__":
    main()

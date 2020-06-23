"""Requires the external libraries matplotlib, seaborn and pandas."""
from datetime import date, timedelta
import json
from pathlib import Path

import pandas as pd
import seaborn as sns
from dateutil import parser
from matplotlib import pyplot as plt, style, pylab as pylab
from matplotlib.ticker import MultipleLocator

import sql_query as sql


def layout():
    """Defines the basic layout for all charts"""
    style.use('seaborn')
    plt.style.use('seaborn-muted')
    plt.rcParams['axes.xmargin'] = 0.01
    # plt.rcParams['axes.ymargin'] = 0.04
    params = {'legend.fontsize': 'small',
              'figure.figsize': (8.5, 5),
              'axes.labelsize': 'small',
              'axes.titlesize': 'medium',
              'xtick.labelsize': 'small',
              'ytick.labelsize': 'small'}
    pylab.rcParams.update(params)


def first_day_previous_month():
    """Returns the date of the first day of the previous month"""
    today = date.today()
    first_day_this_month = date(today.year, today.month, 1)
    last_day_of_the_previous_month = first_day_this_month - timedelta(1)
    first_day_of_the_previous_month = date(
        last_day_of_the_previous_month.year,
        last_day_of_the_previous_month.month, 1)
    return first_day_of_the_previous_month


def change_game_title(sql_result):
    """Changes game title that are too long to be displayed in the chart"""
    shortened_title_names = ["Skyrim VR", "The Walking Dead", "Hot Dogs", "Rick and Morty"]
    games_list = []
    for appid, game_title, max_players, avg_players in sql_result:
        for short_title in shortened_title_names:
            if short_title in game_title:
                games_list.append((appid, short_title, max_players, avg_players))
                break
        else:
            games_list.append((appid, game_title, max_players, avg_players))
    return games_list


def create_json_file(sql_result, file_name):
    data = []
    for x, y in sql_result:
        data.append({
            'x': x,
            'y': round(y)
        })
    json_path = Path.cwd().parent.joinpath("js_charts", file_name)
    with json_path.open(mode='w') as outfile:
        json.dump(data, outfile, indent=4)


def line_chart_plot(sql_result, chart_title, legend=""):
    """Creates a line chart which with the matplotlib library."""
    date_x = []
    players_y = []
    location = "upper left"
    for daily_date, players in sql_result:
        if len(daily_date) > 2:
            daily_date = parser.parse(daily_date)  # formatting string into date
        date_x.append(daily_date)
        players_y.append(players)
    # print(players_y)
    # print(date_x)
    plt.title(chart_title)
    if legend:
        plt.plot(date_x, players_y, label=legend)
        plt.legend(loc=location)
    else:
        plt.plot(date_x, players_y)
    plt.grid(True)
    # plt.tight_layout()


def line_charts(starting_date):
    """Creates the line charts with the data from the sql queries and saves them"""

    # Chart 1
    chart_title = "Steam VR usage based on the monthly average " \
                  "of the daily maximum number of concurrent users (sum of all VR only games)"
    sql_result = sql.peak_players()
    line_chart_plot(sql_result, chart_title)
    create_json_file(sql_result, "avg_peak_over_time.json")
    plt.savefig('../images/avg_peak_over_time.png')

    # # Chart 2
    # plt.subplots()
    # chart_title = "VR usage of the last 6 months based on the daily " \
    #               "peak values of all Steam VR only games"
    # months = ("2019-12", "2020-01", "2020-02", "2020-03", "2020-04", "2020-05")
    # for month in months:
    #     sql_result = sql.max_peak_players_monthly(month)
    #     line_chart_plot(sql_result, chart_title, month)
    # plt.savefig('../images/monthly_vrusage.png')
    #
    # # Chart 3
    # plt.subplots()
    # chart_title = "The number of concurrent users on Steam VR for some games"
    # sql_result = sql.top10_previous_month(starting_date)
    # for appid, name, *_ in sql_result[0:8]:
    #     if appid != 546560 and appid != 823500:
    #         line_chart_plot(sql.max_peak_players(appid), chart_title, name)
    # plt.savefig('../images/max_peak.png')


def bar_chart_plot(sql_result, chart_title, labels):
    """Creates a chart of the 10 most used VR games since 2020 with the seaborn library."""

    # Defines the used graphic style and reduces the text size to fit all information on the chart
    sns.set_style("whitegrid")
    sns.set(font_scale=0.7)

    # Initialize the matplotlib figure
    fig, ax = plt.subplots()

    # Creates a Panda data frame with the data from the sqlite database
    top10 = pd.DataFrame(sql_result, columns=['appid', 'game', 'max_players', 'avg_players'])

    # Plot the maximum number of players
    if labels[1]:
        sns.set_color_codes("pastel")
    else:
        sns.set_color_codes("muted")
    scaling_xaxis = 2500
    ax.xaxis.set_major_locator(MultipleLocator(scaling_xaxis))
    fig = sns.barplot(x="max_players", y="game", data=top10,
                      label=labels[0], color="b")
    fig.axes.set_title(f'{chart_title}', fontsize=10)
    fig.set_xlabel("")
    fig.set_ylabel("")

    # Plot the average number of players
    if labels[1]:
        sns.set_color_codes("muted")
        scaling_xaxis = 200
        ax.xaxis.set_major_locator(MultipleLocator(scaling_xaxis))
        fig = sns.barplot(x="avg_players", y="game", data=top10, label=labels[1], color="b")
        fig.set_xlabel("")
        fig.set_ylabel("")

    # Add a legend and informative axis label
    ax.legend(ncol=2, loc="lower right", frameon=False)
    sns.despine(left=True, bottom=True)


def bar_charts(starting_date):
    """Creates the bar charts with the data from the sql queries and saves them"""

    # Chart 1
    previous_month = starting_date.strftime("%B %Y")
    month = starting_date.strftime("%B")
    chart_title = f"The most played Steam VR games in {previous_month}"
    labels = (f'The maximum number of concurrent users in {month}',
              f'The average daily peak in {month}')
    sql_result = sql.top10_previous_month(starting_date)
    sql_result = change_game_title(sql_result)
    bar_chart_plot(sql_result, chart_title, labels)
    plt.savefig('../images/top10.png')
    plt.savefig(f'../images/top10_{starting_date.strftime("%Y_%m")}.png')

    # Chart 2
    sql_result = sql.top10()
    sql_result = change_game_title(sql_result)
    chart_title = "Steam VR games with the highest number of concurrent users since 2016"
    labels = ("The maximum number of concurrent users", "")
    bar_chart_plot(sql_result, chart_title, labels)
    plt.savefig('../images/top10_max_peak.png')


def main():
    """Generates Charts with the Matplotlib and Seaborn libraries."""
    print("The charts will be created which can take a few seconds.")
    layout()
    starting_date = first_day_previous_month()
    line_charts(starting_date)
    bar_charts(starting_date)
    sql.close_database()
    plt.show()  # Displays the charts
    print("The charts were successfully saved in the images folder.")


if __name__ == "__main__":
    main()

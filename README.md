# Steam VR Statistics
This project analyses all Steam VR only games and determines the daily number of players since 2016. The required information was obtained via web scraping from https://store.steampowered.com (appid of all VR games) and https://steamdb.info (number of daily players) with [Python](https://www.python.org/ "Python") using the [Requests](https://requests.readthedocs.io/en/master/# "Requests"), [JSON](https://docs.python.org/3/library/json.html "JSON") and [lxml](https://lxml.de/ "lxml") library. The information is stored in a [SQLite](https://www.sqlite.org/index.html "SQLite") database and evaluated with [Matplotlib](https://matplotlib.org/3.1.1/index.html# "Matplotlib") and [Seaborn](https://seaborn.pydata.org/# "Seaborn"). The database I have created with over 1.6 million records is available to everyone and can be used for all kinds of statistics and forecasts.
![Top 10 February](/images/top10_2020_02.png)
![Top 10 last month](/images/top10.png)
![Top 10 since 2016](/images/top10_max_peak.png)
![Monthly Vr usage](/images/monthly_vrusage.png)
![Avg peak over time](/images/avg_peak_over_time.png)
![Max peak](/images/max_peak.png)


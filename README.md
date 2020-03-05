# Steam VR Statistics
Determines all Steam VR only games and the number of players. The required information was obtained from https://steamdb.info (number of daily players) and www.vrlfg.net (appid of all VR games) with Python using the [Requests](https://requests.readthedocs.io/en/master/# "Requests") and [json](https://docs.python.org/3/library/json.html "json") library. The information is stored in a sqlite database and evaluated with [Matplotlib](https://matplotlib.org/3.1.1/index.html# "Matplotlib") and [Seaborn](https://seaborn.pydata.org/# "Seaborn"). The database I have created is available to everyone and can be used for all kinds of statistics and forecasts.
<p align="left">
  <img width="828" height="445" src="https://github.com/Bamux/Steam_VR_Statistics/blob/master/images/vrgames_top10_2020.png">
</p>
<p align="center">
  <img width="754" height="437" src="https://github.com/Bamux/Steam_VR_Statistics/blob/master/images/vrgames_avg_peak_over_time.png">
</p>


import sqlite3

# Database connection
conn = sqlite3.connect('../database/vr_games_database.db')
c = conn.cursor()


def create_database():
    """Creates the tables of the database."""
    with conn:
        c.execute('''CREATE TABLE IF NOT EXISTS vr_games
         (appid integer NOT NULL, title text NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS vr_players
         (appid integer NOT NULL, date text NOT NULL, players integer)''')


def get_all_games():
    """Returns all VR Games as a list"""
    c.execute("select * from vr_games")
    return c.fetchall()


def get_appid(appid):
    """Checks if an appid is already available"""
    c.execute(f'select * from vr_games where appid={appid}')
    return c.fetchone()


def add_game(val):
    """Adds games to the database."""
    with conn:
        c.executemany('INSERT INTO vr_games(appid,title) VALUES (?,?)', val)


def add_players(val):
    """Adds players to the database."""
    with conn:
        c.executemany('''INSERT INTO vr_players(appid,date,players) VALUES(?,?,?)''', val)


def reset_players():
    """Deletes the content of the table."""
    with conn:
        c.execute('DELETE FROM vr_players;')


def last_update():
    """Returns the monthly max peak values of a game as a list."""
    c.execute('SELECT max(date) FROM vr_players')
    return c.fetchone()[0]


def top10():
    """Returns the 10 most played VR games since 2016-03 as a list."""
    c.execute('''
    SELECT vr_players.appid, title, max(players) as Maxplayers, round(avg(players)) as Average from vr_players
    INNER JOIN vr_games ON vr_games.appid = vr_players.appid
    WHERE date != '2019-07-24' and date > '2016-03'
    GROUP by vr_players.appid
    ORDER by Maxplayers DESC
    Limit 10
    ''')
    return c.fetchall()


def top10_previous_month(start_date):
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


def peak_players():
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


def max_peak_players(appid):
    """Returns the monthly max peak values of a game as a list."""
    c.execute(f'''
    SELECT strftime('%Y-%m', date) as new_date, 
    max(players) as average from vr_players
    WHERE appid ='{appid}'  and date >= '2019' and date != '2019-07-24' and date < date('now','start of month')
    GROUP by new_date
    ''')
    return c.fetchall()


def max_peak_players_monthly(month):
    """Returns the monthly peak values (sum) of all games as a list."""
    c.execute(f'''
    SELECT strftime('%d', date), sum(players) from (
    SELECT date, players from vr_players
    WHERE date like '{month}%')
    GROUP by date
    ''')
    return c.fetchall()


def close_database():
    conn.close()

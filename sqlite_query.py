def create_database(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vr_games (appid integer NOT NULL, title text NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vr_players (appid integer NOT NULL, date text NOT NULL, players integer)''')


def check_game(conn, val):
    c = conn.cursor()
    c.execute('SELECT * FROM vr_games WHERE appid=?', val)
    return c.fetchone()


def check_player(conn, val):
    c = conn.cursor()
    c.execute('SELECT max(date) FROM vr_players WHERE appid=?', val)
    return c.fetchone()


def last_update(conn):
    c = conn.cursor()
    c.execute('SELECT max(date) FROM vr_players')
    return c.fetchone()


def add_game(conn, val):
    c = conn.cursor()
    c.executemany('INSERT INTO vr_games(appid,title) VALUES (?,?)', val)
    conn.commit()


def add_players(conn, val):
    c = conn.cursor()
    c.executemany('''INSERT INTO vr_players(appid,date,players) VALUES(?,?,?)''', val)
    conn.commit()


def daily_players_online(conn):
    c = conn.cursor()
    c.execute('''
    SELECT date, sum(players) FROM vr_players
    INNER JOIN vr_games ON vr_games.appid = vr_players.appid
    WHERE date != '2019-07-24'
    GROUP by date
    ORDER by date
    ''')
    return c.fetchall()


def peak_players_online(conn):
    c = conn.cursor()
    c.execute('''
    select Date, avg(Number) as maxnumber from (
    SELECT strftime('%Y-%m', date) as Date, sum(players) as Number FROM vr_players
    WHERE date != '2019-07-24'
    GROUP by date)
    GROUP by Date
    Order by Date
    ''')
    return c.fetchall()


def peak_players_appid(conn, val):
    c = conn.cursor()
    c.execute('''
    select Date, avg(Number) as maxnumber from (
    SELECT strftime('%Y-%m', date) as Date, sum(players) as Number FROM vr_players
    where appid = {} and date != '2019-07-24'
    GROUP by date
    ORDER by Number desc)
    GROUP by Date
    Order by Date
    '''.format(val))
    return c.fetchall()


def top10(conn):
    c = conn.cursor()
    c.execute('''
    SELECT title, max(players) as maxplayers from vr_players
    INNER JOIN vr_games ON vr_games.appid = vr_players.appid
    WHERE date != '2019-07-24' and vr_players.appid != 450110
    Group by vr_players.appid
    Order by maxplayers DESC
    Limit 10
    ''')
    return c.fetchall()


def reset(conn):
    c = conn.cursor()
    c.execute('DELETE FROM vr_games;')
    c.execute('DELETE FROM vr_players;')
    conn.commit()

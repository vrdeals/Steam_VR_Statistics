def create_database(c):
    c.execute('''CREATE TABLE IF NOT EXISTS vr_games (appid integer NOT NULL, title text NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vr_players (appid integer NOT NULL, date text NOT NULL, 
    players real NOT NULL, peak integer NOT NULL)''')


# def check_game(c, val):
#     c.execute('SELECT * FROM vr_games WHERE appid=?', val)
#     return c.fetchone()


def last_update(c):
    c.execute('SELECT max(date) FROM vr_players')
    return c.fetchone()


def add_game(c, val):
    c.execute('''INSERT INTO vr_games(appid,title) VALUES(?,?)''', val)


def add_players(c, val):
    c.execute('''INSERT INTO vr_players(appid,date,players,peak) VALUES(?,?,?,?)''', val)


def avg_players(c):
    c.execute('''
    SELECT date, sum(players) FROM vr_players
    INNER JOIN vr_games ON vr_games.appid = vr_players.appid
    WHERE players >= 1 and date >= "2016-03" and date != "2019-07"
    GROUP by date
    ORDER by date
    ''')
    return c.fetchall()


def reset(c):
    c.execute('DELETE FROM vr_games;')
    c.execute('DELETE FROM vr_players;')

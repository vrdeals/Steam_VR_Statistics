def create_database(c):
    c.execute('''CREATE TABLE IF NOT EXISTS vr_games (appid integer NOT NULL, title text NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vr_players (appid integer NOT NULL, date text NOT NULL, players real)''')


# def check_game(c, val):
#     c.execute('SELECT * FROM vr_games WHERE appid=?', val)
#     return c.fetchone()


def last_update(c):
    c.execute('SELECT max(date) FROM vr_players')
    return c.fetchone()


def add_game(c, val):
    c.execute('''INSERT INTO vr_games(appid,title) VALUES(?,?)''', val)


def add_players(c, val):
    c.execute('''INSERT INTO vr_players(appid,date,players) VALUES(?,?,?)''', val)


def reset(c):
    c.execute('DELETE FROM vr_games;')
    c.execute('DELETE FROM vr_players;')

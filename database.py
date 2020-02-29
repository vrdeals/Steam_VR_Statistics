def create_database(c):
    c.execute('''CREATE TABLE IF NOT EXISTS vr_games (appid integer NOT NULL, title text NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vr_players (appid integer NOT NULL, month text NOT NULL, players real)''')


def check_game(c, val):
    c.execute('SELECT * FROM vr_games WHERE appid=?', val)
    return c.fetchone()


def add_game(c, val):
    c.execute('''INSERT INTO vr_games(appid,title) VALUES(?,?)''', val)
    return c.lastrowid


def add_players(c, val):
    c.execute('''INSERT INTO vr_players(appid,date,players) VALUES(?,?,?)''', val)
    return c.lastrowid

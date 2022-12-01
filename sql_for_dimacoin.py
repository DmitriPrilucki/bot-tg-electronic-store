import sqlite3


db = sqlite3.connect('dimacoin9.db')
cur = db.cursor()


async def db_conn():
    cur.execute("CREATE TABLE IF NOT EXISTS users_count (user_id INTEGER PRIMARY KEY, count INT DEFAULT 0, desc TEXT DEFAULT 'NO', time INT DEFAULT 0)")
    db.commit()


async def new_user(user_id):
    cur.execute("INSERT INTO users_count (user_id) VALUES(?)", (user_id,))
    db.commit()


async def update_count(user_id, money):
    cur.execute(f"UPDATE users_count SET count = count + {money} WHERE user_id = ?", (user_id,))
    db.commit()


async def update_time(user_id, seconds):
    cur.execute(f"UPDATE users_count SET time = time + {seconds} WHERE user_id = ?", (user_id,))
    db.commit()


async def sel_time(user_id):
    x = cur.execute("SELECT time FROM users_count WHERE user_id = ?", (user_id,)).fetchone()
    return x


async def update_count_all(money):
    cur.execute(f"UPDATE users_count SET count = count + {money}")
    db.commit()


async def sel_count(user_id):
    x = cur.execute("SELECT count FROM users_count WHERE user_id = ?", (user_id,)).fetchone()
    return x


async def update_desc(user_id, desc):
    cur.execute('UPDATE users_count SET desc = ? WHERE user_id = ?', (desc, user_id)).fetchone()
    db.commit()


async def sel_desc(user_id):
    x = cur.execute("SELECT desc FROM users_count WHERE user_id = ?", (user_id,)).fetchone()
    return x


async def admin_count():
    cur.execute("UPDATE users_count SET count = 0")
    db.commit()
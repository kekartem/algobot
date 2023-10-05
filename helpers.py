import re
from config import conn, cur, Manager, Request, God


def is_valid_email(email):
    email_regex = re.compile(
        r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    if re.fullmatch(email_regex, email):
        return True
    return False


def is_valid_number(number):
    number_regex = re.compile(r"\+?[0-9\(\)-]*")
    if re.fullmatch(number_regex, number) and len(number) > 10:
        return True
    return False


async def read_all_managers():
    cur.execute('SELECT * FROM managers')
    result = cur.fetchall()
    return list(map(lambda x: Manager(*x), result)) if result is not None else Manager()


async def read_manager_by_id(manager_chat_id):
    cur.execute('SELECT * FROM managers WHERE manager_chat_id = :manager_chat_id',
                                      {'manager_chat_id': manager_chat_id})
    result = cur.fetchone()
    return Manager(*result) if result is not None else Manager()


async def save_manager(manager_chat_id, manager_tg_login):
    cur.execute(
        'INSERT INTO managers(manager_chat_id, manager_tg_login) VALUES (:manager_chat_id, :manager_tg_login)',
        {'manager_chat_id': manager_chat_id, 'manager_tg_login': manager_tg_login})
    conn.commit()


async def remove_manager(manager_chat_id):
    cur.execute('DELETE FROM managers WHERE manager_chat_id = :manager_chat_id',
                           {'manager_chat_id': manager_chat_id})
    conn.commit()


async def read_all_requests():
    cur.execute('SELECT * FROM requests')
    result = cur.fetchall()
    return list(map(lambda x: Request(*x), result)) if result is not None else Request()


async def save_request(name, number, email, user_tg_login):
    cur.execute(
        'INSERT INTO requests(name, number, email, user_tg_login) VALUES(:name, :number, :email, :user_tg_login)',
        {'name': name, 'number': number, 'email': email, 'user_tg_login': user_tg_login})
    conn.commit()


async def read_god_by_id(god_chat_id):
    cur.execute('SELECT * FROM gods WHERE god_chat_id = :god_chat_id', {'god_chat_id': god_chat_id})
    result = cur.fetchone()
    return God(*result) if result is not None else God()


async def save_god(god_chat_id, god_tg_login):
    cur.execute('INSERT INTO gods(god_chat_id, god_tg_login) VALUES(:god_chat_id, :god_tg_login)',
                           {'god_chat_id': god_chat_id, 'god_tg_login': god_tg_login})
    conn.commit()


async def remove_god(god_chat_id):
    cur.execute('DELETE FROM gods WHERE god_chat_id = :god_chat_id', {'god_chat_id': god_chat_id})
    conn.commit()


async def create_tables():
    cur.execute('''CREATE TABLE IF NOT EXISTS managers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manager_chat_id TEXT NOT NULL,
        manager_tg_login TEXT NOT NULL
    );''')
    conn.commit()
    cur.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        number TEXT NOT NULL,
        email TEXT NOT NULL,
        user_tg_login TEXT NOT NULL
    );''')
    conn.commit()
    cur.execute('''CREATE TABLE IF NOT EXISTS gods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        god_chat_id TEXT NOT NULL,
        god_tg_login TEXT NOT NULL
    );''')
    conn.commit()

    
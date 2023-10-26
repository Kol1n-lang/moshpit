import asyncio
import sqlite3 as sq

import os

def prizers():
    with sq.connect('moshpit.db') as con:
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS prizers(
                        user_id INTEGER PRIMARY KEY,
                        user_name VARCHAR(250),
                        first_name VARCHAR(250),
                        last_name VARCHAR(250)
                        );'''
    )
prizers()


def insert_user(user_id, user_name, first_name, last_name, x):
    with sq.connect('moshpit.db') as con:
        cur = con.cursor()
        cur.execute(
            f'''INSERT OR IGNORE INTO users (id, user_id, user_name, first_name, last_name, people) VALUES (?,?,?,?,?,?);''', (None, user_id, user_name, first_name, last_name, x)
        )
def insert_prizes(user_id, user_name, first_name, last_name):
    us = user_id
    na = user_name
    fi = first_name
    la = last_name
    with sq.connect('moshpit.db') as con:
        cur = con.cursor()
        cur.execute(
            f'''INSERT OR IGNORE INTO prizers VALUES(?, ?, ?, ?);''', (us, na, fi, la)
        )
import os

def find_photo_names(photo_name):
    folder_path = 'qr_codes'
    photo_names = []
    for file in os.listdir(folder_path):
        if file.startswith(photo_name):
            photo_names.append(file)
    return photo_names
def counts(user_id, type):
    with sq.connect('moshpit.db') as con:
        cur = con.cursor()
        query = "SELECT COUNT(*) FROM users WHERE user_id = ? and people = ?"
        cur.execute(query, (user_id, type))
        count = cur.fetchone()[0]
        return count

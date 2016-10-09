# -*- coding: utf-8 -*-

SQL = {
    'create_users_table': '''
CREATE TABLE IF NOT EXISTS users_table (
   login_id INTEGER PRIMARY KEY,
   login TEXT,
   access_token TEXT
)''',

    'add_token': 'INSERT INTO users_table (login, access_token) VALUES(?, ?)',
    'get_token': 'SELECT access_token FROM users_table WHERE login = ?',
    'rm_token': 'DELETE FROM users_table WHERE login = ?'
}

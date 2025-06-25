import sqlite3
import os

DATABASE = 'todo.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
   ALTER TABLE agendas RENAME COLUMN done TO ativo;

    ''')

    conn.commit()
    conn.close()

if not os.path.exists(DATABASE):
    init_db()

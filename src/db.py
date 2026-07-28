import sqlite3
def get_connection(db_path='caral_facts.sqlite'):
    return sqlite3.connect(db_path)
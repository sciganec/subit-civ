import sqlite3

def get_connection(db_path='caral_facts.sqlite'):
    """Return a connection to the SQLite database."""
    return sqlite3.connect(db_path)
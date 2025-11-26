import sqlite3


DATABASE_URL = "intellidoc.sqlite3"

COLLECTIONS_SCHEMA = """CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL
);"""

DOCUMENTS_SCHEMA = """CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    upload_path TEXT NOT NULL,
    collection_id INTEGER NOT NULL,
    FOREIGN KEY (collection_id)
        REFERENCES collections (id)
);"""


class DatabaseHandler:
    def __init__(self):
        conn = sqlite3.connect(DATABASE_URL)
        self.sqlite_cursor = conn.cursor()

        self.sqlite_cursor.execute(COLLECTIONS_SCHEMA)
        self.sqlite_cursor.execute(DOCUMENTS_SCHEMA)

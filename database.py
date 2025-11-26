import sqlite3
from dataclasses import dataclass
from datetime import datetime

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


@dataclass
class Collection:
    id: int
    name: str
    created_at: datetime


@dataclass
class Document:
    id: int
    filename: str
    status: str


class DatabaseHandler:
    """Main class to interface with the SQLite Database"""

    def __init__(self):
        self.sqlite_conn = sqlite3.connect(DATABASE_URL, autocommit=True)
        self.sqlite_cursor = self.sqlite_conn.cursor()

        self.sqlite_cursor.execute(COLLECTIONS_SCHEMA)
        self.sqlite_cursor.execute(DOCUMENTS_SCHEMA)

        self.sqlite_conn.autocommit

    def create_collection(self, name: str):
        """Creates a collection with the given name"""
        current_time = datetime.now()
        self.sqlite_cursor.execute(
            "INSERT INTO collections (name, created_at) VALUES (?, ?);",
            (name, current_time.isoformat()),
        )

    def get_collections(self) -> list[Collection]:
        """Returns all collections in the database"""
        self.sqlite_cursor.execute("SELECT id, name, created_at FROM collections;")
        rows = self.sqlite_cursor.fetchall()
        return [
            Collection(
                id=row[0], name=row[1], created_at=datetime.fromisoformat(row[2])
            )
            for row in rows
        ]

    def get_collection_by_id(self, collection_id: int) -> Collection | None:
        """Returns a collection with the given ID. If a collection with the given ID doesn't exist, it simply returns None"""
        self.sqlite_cursor.execute(
            "SELECT id, name, created_at FROM collections WHERE id = ?;",
            (collection_id,),
        )
        row = self.sqlite_cursor.fetchone()
        if row:
            return Collection(
                id=row[0], name=row[1], created_at=datetime.fromisoformat(row[2])
            )
        return None

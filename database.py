import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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

JOBS_SCHEMA = """CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT
);
    """


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
    upload_path: str

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job:
    def __init__(self, filename: str):
        self.id = str(uuid.uuid4())
        self.filename = filename
        self.status = JobStatus.QUEUED
        self.result = None


class SqliteDatabase:
    """Main class to interface with the SQLite Database"""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_URL, autocommit=True)
        self.cursor = self.conn.cursor()

        self.cursor.execute(COLLECTIONS_SCHEMA)
        self.cursor.execute(DOCUMENTS_SCHEMA)
        self.cursor.execute(JOBS_SCHEMA)

        self.conn.autocommit

    def create_collection(self, name: str):
        """Creates a collection with the given name"""
        current_time = datetime.now()
        self.cursor.execute(
            "INSERT INTO collections (name, created_at) VALUES (?, ?);",
            (name, current_time.isoformat()),
        )

    def get_collections(self) -> list[Collection]:
        """Returns all collections in the database"""
        self.cursor.execute("SELECT id, name, created_at FROM collections;")
        rows = self.cursor.fetchall()
        return [
            Collection(
                id=row[0], name=row[1], created_at=datetime.fromisoformat(row[2])
            )
            for row in rows
        ]

    def get_collection_by_id(self, collection_id: int) -> Collection | None:
        """Returns a collection with the given ID. If a collection with the given ID doesn't exist, it simply returns None"""
        self.cursor.execute(
            "SELECT id, name, created_at FROM collections WHERE id = ?;",
            (collection_id,),
        )
        row = self.cursor.fetchone()
        if row:
            return Collection(
                id=row[0], name=row[1], created_at=datetime.fromisoformat(row[2])
            )
        return None

    def add_document(
        self, filename: str, status: str, upload_path: str, collection_id: int
    ) -> int:
        """Adds a document to the database"""
        self.cursor.execute(
            "INSERT INTO documents (filename, status, upload_path, collection_id) VALUES (?, ?, ?, ?);",
            (filename, status, upload_path, collection_id),
        )
        return self.cursor.lastrowid

    def modify_document(
        self,
        document_id: int,
        filename: str = None,
        status: str = None,
        upload_path: str = None,
    ):
        """Modifies an existing document in the database"""
        updates = []
        params = []

        if filename is not None:
            updates.append("filename = ?")
            params.append(filename)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if upload_path is not None:
            updates.append("upload_path = ?")
            params.append(upload_path)

        if not updates:
            raise ValueError("No fields to update")

        params.append(document_id)
        query = f"UPDATE documents SET {', '.join(updates)} WHERE id = ?;"
        self.cursor.execute(query, params)

    def get_document_count(self, collection_id: int) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM documents WHERE collection_id = ?", (collection_id,))
        return self.cursor.fetchone()[0]

    def get_documents(self, id: int) -> list[Document]:
        self.cursor.execute("SELECT id, filename, status, upload_path FROM documents WHERE collection_id = ?", (id,))
        return [
            Document(id=row[0], filename=row[1], status=row[2], upload_path=row[3]) for row in self.cursor.fetchall()
        ]

    def get_document(self, id: int) -> Document | None:
        self.cursor.execute("SELECT id, filename, status, upload_path FROM documents WHERE id = ?", (id,))
        row = self.cursor.fetchone()
        return Document(id=row[0], filename=row[1], status=row[2], upload_path=row[3])

    def add_job(self, job: Job):
        """Adds the given job to the job store"""
        self.cursor.execute(
            "INSERT INTO jobs (id, filename, status) VALUES (?, ?, ?);",
            (job.id, job.filename, job.status)
        )

    def get_job(self, job_id: str) -> Job | None:
        self.cursor.execute("SELECT id, filename, status, result FROM jobs WHERE id = ?;", (job_id,))
        row = self.cursor.fetchone()
        if row:
            job = Job(filename=row[1])
            job.id = row[0]
            job.status = JobStatus(row[2])
            job.result = row[3]
            return job
        else:
            return None
    
    def update_job(self, job_id: int, filename: str = None, result: str = None, status: JobStatus = None):
        updates = []
        params = []

        if filename is not None:
            updates.append("filename = ?")
            params.append(filename)
        if result is not None:
            updates.append("result = ?")
            params.append(result)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        params.append(job_id)
        query = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, params)

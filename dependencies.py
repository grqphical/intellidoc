"""All dependecies to be injected into FastAPI"""
from vector_database import VectorDatabase
from database import SqliteDatabase
from functools import lru_cache

@lru_cache()
def get_vector_db() -> VectorDatabase:
    """Dependency provider for the vector database

    FastAPI will inject this into every request

    We use lru_cache so that Python caches the database connection rather than make a new one every time
    """
    return VectorDatabase()

@lru_cache()
def get_sqlite_db() -> SqliteDatabase:
    """Dependency provider for the Sqlite database

    FastAPI will inject this into every request

    We use lru_cache so that Python caches the database connection rather than make a new one every time
    """
    return SqliteDatabase()

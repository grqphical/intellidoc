"""All dependecies to be injected into FastAPI"""
from vector_database import VectorDatabase
from database import SqliteDatabase, DATABASE_URL
from functools import lru_cache

import sqlite3

@lru_cache()
def get_vector_db() -> VectorDatabase:
    """Dependency provider for the vector database

    FastAPI will inject this into every request

    We use lru_cache so that Python caches the database connection rather than make a new one every time
    """
    return VectorDatabase()

def get_sqlite_db() -> SqliteDatabase:
    """
    Dependency provider for the Sqlite Database.
    """
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row 
    
    try:
        db_instance = SqliteDatabase(conn)
        yield db_instance
        
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


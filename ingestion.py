"""Script that contains all of the classes and functions needed for the document ingestion pipeline"""

import uuid
import asyncio
from enum import Enum
from pathlib import Path
from typing import Dict
from database import DatabaseHandler

MAX_CONCURRENT_JOBS = asyncio.Semaphore(2)


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


async def ingest_document(
    job_id: str,
    file_path: Path,
    document_id: int,
    job_store: Dict[str, Job],
    db: DatabaseHandler,
):
    """This function takes a document in the queue, chunks it, embeds each
    chunk into a vector and saves it into the vector database.

    Right now it only simulates the embedding and vector database by waiting a few seconds
    """
    job = job_store[job_id]
    async with MAX_CONCURRENT_JOBS:
        try:
            job.status = JobStatus.PROCESSING
            db.modify_document(document_id, status=JobStatus.PROCESSING)
            print(f"[{job_id}] Starting ingestion for {job.filename}...")

            # simulation of running the model
            await asyncio.sleep(5)

            job.result = f"Ran job for {job.filename}"
            job.status = JobStatus.COMPLETED
            print(f"[{job_id}] Finished.")

        except Exception as e:
            job.status = JobStatus.FAILED
            job.result = str(e)
            db.modify_document(document_id, status=JobStatus.FAILED)
        finally:
            # Cleanup temp file
            if file_path.exists():
                file_path.unlink()
            db.modify_document(document_id, status=JobStatus.COMPLETED)

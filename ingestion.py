"""Script that contains all of the classes and functions needed for the document ingestion pipeline"""

import asyncio
from pathlib import Path
from database import DatabaseHandler, JobStatus

MAX_CONCURRENT_JOBS = asyncio.Semaphore(2)




async def ingest_document(
    job_id: str,
    file_path: Path,
    document_id: int,
    db: DatabaseHandler,
):
    """This function takes a document in the queue, chunks it, embeds each
    chunk into a vector and saves it into the vector database.

    Right now it only simulates the embedding and vector database by waiting a few seconds
    """
    print(job_id)
    job = db.get_job(job_id)
    async with MAX_CONCURRENT_JOBS:
        try:
            job.status = JobStatus.PROCESSING
            db.update_job(job.id, status=job.status)
            db.modify_document(document_id, status=JobStatus.PROCESSING)
            print(f"[{job_id}] Starting ingestion for {job.filename}...")

            # simulation of running the model
            await asyncio.sleep(5)

            job.result = f"Ran job for {job.filename}"
            job.status = JobStatus.COMPLETED
            print(f"[{job_id}] Finished.")
            db.modify_document(document_id, status=JobStatus.COMPLETED)

        except Exception as e:
            job.status = JobStatus.FAILED
            job.result = str(e)
            db.modify_document(document_id, status=JobStatus.FAILED)
        finally:
            # Cleanup temp file
            if file_path.exists():
                file_path.unlink()
            db.update_job(job_id, status=job.status, result=job.result)

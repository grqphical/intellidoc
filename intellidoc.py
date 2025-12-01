from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Request,
    Form,
    HTTPException,
    UploadFile,
    Depends,
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import SqliteDatabase, Job, JobStatus, DATABASE_URL, COLLECTIONS_SCHEMA, DOCUMENTS_SCHEMA, JOBS_SCHEMA
from dependencies import get_sqlite_db, get_vector_db
from ingestion import ingest_document
from typing import Annotated
from vector_database import VectorDatabase

import sqlite3
import shutil

def init_tables():
    """Helper to run migrations on startup"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(COLLECTIONS_SCHEMA)
    cursor.execute(DOCUMENTS_SCHEMA)
    cursor.execute(JOBS_SCHEMA)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_tables()
    yield

templates = Jinja2Templates(directory="templates")

app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)

VectorDBDependency = Annotated[SqliteDatabase, Depends(get_vector_db)]
SqliteDBDependency = Annotated[VectorDatabase, Depends(get_sqlite_db)]


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/api/collection")
async def create_collection(request: Request, name: Annotated[str, Form], sqlite_db: SqliteDBDependency):
    try:
        sqlite_db.create_collection(name)
    except sqlite3.IntegrityError as e:
        # a collection with the same name exists already
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Collection with name {name} already exists"
            )
    collections = sqlite_db.get_collections()
    return templates.TemplateResponse(
        request=request,
        name="collection_list.html",
        context={"collections": collections},
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, sqlite_db: SqliteDBDependency):
    collections = sqlite_db.get_collections()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"collections": collections}
    )


@app.get("/collection/{collection_id}", response_class=HTMLResponse)
async def get_collection(request: Request, collection_id: int, sqlite_db: SqliteDBDependency):
    collection = sqlite_db.get_collection_by_id(collection_id)
    if collection == None:
        raise HTTPException(status_code=404, detail="Collection Not Found")
    

    collection_count = sqlite_db.get_document_count(collection_id)

    documents = sqlite_db.get_documents(collection_id)
    return templates.TemplateResponse(
        request=request, name="collection.html", context={"collection": collection, "collectionCount": collection_count, "documents": documents}
    )


@app.post("/api/collection/{collection_id}/upload", response_class=HTMLResponse)
async def upload_file(
    request: Request, collection_id: int, background_tasks: BackgroundTasks, sqlite_db: SqliteDBDependency, file: UploadFile = File(...), 
):
    job = Job(filename=file.filename)
    sqlite_db.add_job(job)

    # save file temporarily on disk
    temp_dir = Path("uploads")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / f"{job.id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document_id = sqlite_db.add_document(
        file.filename, JobStatus.QUEUED, file_path.absolute().as_posix(), collection_id
    )

    background_tasks.add_task(
        ingest_document,
        job.id,
        file_path,
        document_id,
        sqlite_db,
    )

    documents = sqlite_db.get_documents(collection_id)

    return templates.TemplateResponse(
        request=request, name="document_list.html", context={"documents": documents, "collectionId": collection_id}
    )

@app.get("/collection/{collection_id}/status", response_class=HTMLResponse)
async def get_document_status(
    request: Request, collection_id: int, sqlite_db: SqliteDBDependency
):
    
    documents = sqlite_db.get_documents(collection_id)

    return templates.TemplateResponse(
        request=request, name="document_list.html", context={"documents": documents, "collectionId": collection_id}
    )

@app.get("/documents/{document_id}/download")
async def download_document(document_id: int, sqlite_db: SqliteDBDependency):
    document = sqlite_db.get_document(document_id)

    if not document:
        raise HTTPException(status_code=404, detail='Document Not Found')

    return FileResponse(document.upload_path)

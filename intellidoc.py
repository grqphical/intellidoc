from pathlib import Path
import shutil
from typing import Annotated

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Request,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import DatabaseHandler, Job, JobStatus
from ingestion import ingest_document

import sqlite3

app = FastAPI(docs_url=None, redoc_url=None)

app.state.db = DatabaseHandler()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.post("/api/collection")
async def create_collection(request: Request, name: Annotated[str, Form()]):
    try:
        app.state.db.create_collection(name)
    except sqlite3.IntegrityError as e:
        # a collection with the same name exists already
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Collection with name {name} already exists"
            )
    collections = app.state.db.get_collections()
    return templates.TemplateResponse(
        request=request,
        name="collection_list.html",
        context={"collections": collections},
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    collections = app.state.db.get_collections()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"collections": collections}
    )


@app.get("/collection/{collection_id}", response_class=HTMLResponse)
async def get_collection(request: Request, collection_id: int):
    collection = app.state.db.get_collection_by_id(collection_id)
    if collection == None:
        raise HTTPException(status_code=404, detail="Collection Not Found")
    

    collection_count = app.state.db.get_document_count(collection_id)

    documents = app.state.db.get_documents(collection_id)
    return templates.TemplateResponse(
        request=request, name="collection.html", context={"collection": collection, "collectionCount": collection_count, "documents": documents}
    )


@app.post("/api/collection/{collection_id}/upload", response_class=HTMLResponse)
async def upload_file(
    request: Request, collection_id: int, background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    job = Job(filename=file.filename)
    app.state.db.add_job(job)

    # save file temporarily on disk
    temp_dir = Path("uploads")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / f"{job.id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document_id = app.state.db.add_document(
        file.filename, JobStatus.QUEUED, file_path.absolute().as_posix(), collection_id
    )

    background_tasks.add_task(
        ingest_document,
        job.id,
        file_path,
        document_id,
        app.state.db,
    )

    documents = app.state.db.get_documents(collection_id)

    return templates.TemplateResponse(
        request=request, name="document_list.html", context={"documents": documents, "collectionId": collection_id}
    )

@app.get("/collection/{collection_id}/status", response_class=HTMLResponse)
async def get_document_status(
    request: Request, collection_id: int
):
    
    documents = app.state.db.get_documents(collection_id)

    return templates.TemplateResponse(
        request=request, name="document_list.html", context={"documents": documents, "collectionId": collection_id}
    )



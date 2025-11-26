from typing import Annotated

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import DatabaseHandler

import sqlite3

app = FastAPI()

app.state.db = DatabaseHandler()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.post("/api/collection")
async def upload_file(request: Request, name: Annotated[str, Form()]):
    try:
        app.state.db.create_collection(name)
    except sqlite3.IntegrityError as e:
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


@app.get("/collections/{collection_id}", response_class=HTMLResponse)
async def root(request: Request, collection_id: int):
    collection = app.state.db.get_collection_by_id(collection_id)
    if collection == None:
        raise HTTPException(status_code=404, detail="Collection Not Found")

    return templates.TemplateResponse(
        request=request, name="collection.html", context={"collection": collection}
    )

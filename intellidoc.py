from fastapi import FastAPI
from database import DatabaseHandler

app = FastAPI()

app.state.db = DatabaseHandler()


@app.get("/")
async def root():
    return {"message": "Hello World"}

from fastapi import FastAPI

from app.db.database import engine

app = FastAPI(title="AI Meeting Assistant")


@app.get("/")
async def root():
    return {"message": "AI Meeting Assistant"}


@app.get("/health")
async def health():
    async with engine.connect():
        return {"status": "ok"}
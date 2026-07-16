from fastapi import FastAPI
from app.database import engine

app = FastAPI(
    title="MentorMind AI",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected"
    }
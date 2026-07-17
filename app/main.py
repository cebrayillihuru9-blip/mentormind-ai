from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
import app.models

from app.routers import users, mentors, bookings, reviews, dashboard


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="MentorMind AI",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(mentors.router)
app.include_router(bookings.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected"
    }
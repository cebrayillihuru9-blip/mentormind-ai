from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
import app.models

from app.routers import users, mentors, bookings, reviews, dashboard, ai, admin

Base.metadata.create_all(bind=engine)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="MentorMind AI",
    description="AI-supported mentor discovery and learning platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
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
app.include_router(ai.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {
        "name": "MentorMind AI",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected",
    }



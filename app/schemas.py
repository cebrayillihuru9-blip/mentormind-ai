from datetime import date

from pydantic import BaseModel, EmailStr, Field


# =========================
# USER
# =========================

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True


# =========================
# MENTOR
# =========================

class MentorCreate(BaseModel):
    name: str
    expertise: str
    bio: str
    hourly_rate: float


class MentorUpdate(BaseModel):
    name: str
    expertise: str
    bio: str
    hourly_rate: float


class MentorResponse(BaseModel):
    id: int
    name: str
    expertise: str
    bio: str
    hourly_rate: float
    owner_id: int

    # Gün 10 üçün yeni sahələr
    average_rating: float | None = None
    reviews_count: int = 0

    class Config:
        from_attributes = True


# =========================
# BOOKING
# =========================

class BookingCreate(BaseModel):
    mentor_id: int
    booking_date: date


class BookingResponse(BaseModel):
    id: int
    mentor_id: int
    user_id: int
    booking_date: date
    status: str

    class Config:
        from_attributes = True
class BookingStatusUpdate(BaseModel):
    status: str

# =========================
# REVIEW
# =========================

class ReviewCreate(BaseModel):
    mentor_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str


class ReviewResponse(BaseModel):
    id: int
    mentor_id: int
    user_id: int
    rating: int
    comment: str

    class Config:
        from_attributes = True
from datetime import date

from pydantic import BaseModel, EmailStr, Field


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


class MentorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    expertise: str = Field(..., min_length=2, max_length=150)
    bio: str = Field(..., min_length=5, max_length=1500)
    hourly_rate: float = Field(..., gt=0, le=10000)


class MentorUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    expertise: str = Field(..., min_length=2, max_length=150)
    bio: str = Field(..., min_length=5, max_length=1500)
    hourly_rate: float = Field(..., gt=0, le=10000)


class MentorResponse(BaseModel):
    id: int
    name: str
    expertise: str
    bio: str | None = None
    hourly_rate: float
    owner_id: int | None = None
    average_rating: float | None = None
    reviews_count: int = 0

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    mentor_id: int
    booking_date: date


class BookingResponse(BaseModel):
    id: int
    mentor_id: int
    user_id: int
    booking_date: date
    status: str

    mentor_name: str | None = None
    mentor_expertise: str | None = None
    hourly_rate: float | None = None

    user_name: str | None = None
    user_email: str | None = None

    class Config:
        from_attributes = True


class BookingStatusUpdate(BaseModel):
    status: str


class ReviewCreate(BaseModel):
    mentor_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=1000)


class ReviewResponse(BaseModel):
    id: int
    mentor_id: int
    user_id: int
    rating: int
    comment: str
    mentor_name: str | None = None
    user_name: str | None = None

    class Config:
        from_attributes = True

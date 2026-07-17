from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    Date
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    mentors = relationship(
        "Mentor",
        back_populates="owner"
    )

    bookings = relationship(
        "Booking",
        back_populates="user"
    )

    reviews = relationship(
        "Review",
        back_populates="user"
    )


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    expertise = Column(String, nullable=False)
    bio = Column(Text)
    hourly_rate = Column(Float)

    owner_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    owner = relationship(
        "User",
        back_populates="mentors"
    )

    bookings = relationship(
        "Booking",
        back_populates="mentor"
    )

    reviews = relationship(
        "Review",
        back_populates="mentor"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    booking_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        default="pending"
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    mentor_id = Column(
        Integer,
        ForeignKey("mentors.id")
    )

    user = relationship(
        "User",
        back_populates="bookings"
    )

    mentor = relationship(
        "Mentor",
        back_populates="bookings"
    )


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    rating = Column(
        Integer,
        nullable=False
    )

    comment = Column(
        Text,
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    mentor_id = Column(
        Integer,
        ForeignKey("mentors.id")
    )

    user = relationship(
        "User",
        back_populates="reviews"
    )

    mentor = relationship(
        "Mentor",
        back_populates="reviews"
    )
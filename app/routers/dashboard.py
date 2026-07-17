from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.auth import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/user")
def user_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    total_bookings = db.query(models.Booking).filter(
        models.Booking.user_id == current_user.id
    ).count()


    pending_bookings = db.query(models.Booking).filter(
        models.Booking.user_id == current_user.id,
        models.Booking.status == "pending"
    ).count()


    accepted_bookings = db.query(models.Booking).filter(
        models.Booking.user_id == current_user.id,
        models.Booking.status == "accepted"
    ).count()


    completed_bookings = db.query(models.Booking).filter(
        models.Booking.user_id == current_user.id,
        models.Booking.status == "completed"
    ).count()


    return {
        "user_id": current_user.id,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "accepted_bookings": accepted_bookings,
        "completed_bookings": completed_bookings
    }



@router.get("/mentor")
def mentor_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    total_mentors = db.query(models.Mentor).filter(
        models.Mentor.owner_id == current_user.id
    ).count()


    total_bookings = (
        db.query(models.Booking)
        .join(
            models.Mentor,
            models.Booking.mentor_id == models.Mentor.id
        )
        .filter(
            models.Mentor.owner_id == current_user.id
        )
        .count()
    )


    total_reviews = (
        db.query(models.Review)
        .join(
            models.Mentor,
            models.Review.mentor_id == models.Mentor.id
        )
        .filter(
            models.Mentor.owner_id == current_user.id
        )
        .count()
    )


    average_rating = (
        db.query(func.avg(models.Review.rating))
        .join(
            models.Mentor,
            models.Review.mentor_id == models.Mentor.id
        )
        .filter(
            models.Mentor.owner_id == current_user.id
        )
        .scalar()
    )


    pending_bookings = (
        db.query(models.Booking)
        .join(
            models.Mentor,
            models.Booking.mentor_id == models.Mentor.id
        )
        .filter(
            models.Mentor.owner_id == current_user.id,
            models.Booking.status == "pending"
        )
        .count()
    )


    accepted_bookings = (
        db.query(models.Booking)
        .join(
            models.Mentor,
            models.Booking.mentor_id == models.Mentor.id
        )
        .filter(
            models.Mentor.owner_id == current_user.id,
            models.Booking.status == "accepted"
        )
        .count()
    )


    completed_bookings = (
        db.query(models.Booking)
        .join(
            models.Mentor,
            models.Booking.mentor_id == models.Mentor.id
        )
        .filter(
            models.Mentor.owner_id == current_user.id,
            models.Booking.status == "completed"
        )
        .count()
    )


    total_income = (
        db.query(func.sum(models.Mentor.hourly_rate))
        .join(
            models.Booking,
            models.Booking.mentor_id == models.Mentor.id
        )
        .filter(
            models.Mentor.owner_id == current_user.id,
            models.Booking.status == "completed"
        )
        .scalar()
    )


    return {
        "user_id": current_user.id,
        "total_mentors": total_mentors,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "accepted_bookings": accepted_bookings,
        "completed_bookings": completed_bookings,
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "total_income": total_income or 0
    }
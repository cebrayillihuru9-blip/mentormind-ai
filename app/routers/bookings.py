from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


def booking_payload(booking: models.Booking):
    mentor = booking.mentor
    user = booking.user

    return {
        "id": booking.id,
        "mentor_id": booking.mentor_id,
        "user_id": booking.user_id,
        "booking_date": booking.booking_date,
        "status": booking.status,
        "mentor_name": mentor.name if mentor else None,
        "mentor_expertise": (
            mentor.expertise if mentor else None
        ),
        "hourly_rate": (
            mentor.hourly_rate if mentor else None
        ),
        "user_name": user.full_name if user else None,
        "user_email": user.email if user else None,
    }


@router.post(
    "/",
    response_model=schemas.BookingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if booking.booking_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Past dates cannot be booked"
        )

    mentor = (
        db.query(models.Mentor)
        .filter(models.Mentor.id == booking.mentor_id)
        .first()
    )

    if mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )

    if mentor.owner_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot book your own mentor profile"
        )

    duplicate = (
        db.query(models.Booking)
        .filter(
            models.Booking.user_id == current_user.id,
            models.Booking.mentor_id == booking.mentor_id,
            models.Booking.booking_date == booking.booking_date,
            models.Booking.status.in_(["pending", "accepted"])
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="You already booked this mentor for this date"
        )

    db_booking = models.Booking(
        mentor_id=booking.mentor_id,
        user_id=current_user.id,
        booking_date=booking.booking_date,
        status="pending"
    )

    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    return booking_payload(db_booking)


@router.get(
    "/",
    response_model=list[schemas.BookingResponse]
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .order_by(
            models.Booking.booking_date.desc(),
            models.Booking.id.desc()
        )
        .all()
    )

    return [
        booking_payload(booking)
        for booking in bookings
    ]


@router.get(
    "/mentor/my-bookings",
    response_model=list[schemas.BookingResponse]
)
def get_my_mentor_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    bookings = (
        db.query(models.Booking)
        .join(
            models.Mentor,
            models.Booking.mentor_id == models.Mentor.id
        )
        .filter(models.Mentor.owner_id == current_user.id)
        .order_by(
            models.Booking.booking_date.desc(),
            models.Booking.id.desc()
        )
        .all()
    )

    return [
        booking_payload(booking)
        for booking in bookings
    ]


@router.get(
    "/{booking_id}",
    response_model=schemas.BookingResponse
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    is_student = booking.user_id == current_user.id
    is_mentor = (
        booking.mentor is not None
        and booking.mentor.owner_id == current_user.id
    )

    if not is_student and not is_mentor:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this booking"
        )

    return booking_payload(booking)


@router.put(
    "/{booking_id}/status",
    response_model=schemas.BookingResponse
)
def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if (
        booking.mentor is None
        or booking.mentor.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the mentor can update this booking"
        )

    allowed_statuses = {
        "accepted",
        "rejected",
        "completed"
    }

    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid booking status"
        )

    if (
        status_update.status == "completed"
        and booking.status != "accepted"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only accepted bookings can be completed"
        )

    booking.status = status_update.status

    db.commit()
    db.refresh(booking)

    return booking_payload(booking)


@router.put(
    "/{booking_id}/cancel",
    response_model=schemas.BookingResponse
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot cancel this booking"
        )

    if booking.status in {"completed", "rejected", "cancelled"}:
        raise HTTPException(
            status_code=400,
            detail="This booking cannot be cancelled"
        )

    booking.status = "cancelled"

    db.commit()
    db.refresh(booking)

    return booking_payload(booking)

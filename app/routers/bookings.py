from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


@router.post("/", response_model=schemas.BookingResponse)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    mentor = db.query(models.Mentor).filter(
        models.Mentor.id == booking.mentor_id
    ).first()


    if mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )


    db_booking = models.Booking(
        mentor_id=booking.mentor_id,
        user_id=current_user.id,
        booking_date=booking.booking_date
    )


    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)


    return db_booking



@router.get("/", response_model=list[schemas.BookingResponse])
def get_bookings(
    db: Session = Depends(get_db)
):

    return db.query(models.Booking).all()



@router.get("/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):

    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id
    ).first()


    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )


    return booking



@router.get("/mentor/my-bookings", response_model=list[schemas.BookingResponse])
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
        .filter(
            models.Mentor.owner_id == current_user.id
        )
        .all()
    )


    return bookings



@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id
    ).first()


    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )


    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this booking"
        )


    db.delete(booking)
    db.commit()


    return {
        "message": "Booking deleted successfully"
    }
@router.put("/{booking_id}/status", response_model=schemas.BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id
    ).first()


    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )


    if booking.mentor.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this booking"
        )


    allowed_statuses = [
        "pending",
        "accepted",
        "rejected",
        "completed"
    ]


    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid booking status"
        )


    booking.status = status_update.status

    db.commit()
    db.refresh(booking)


    return booking
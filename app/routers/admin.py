from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.database import get_db


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


class MakeMentorRequest(BaseModel):
    expertise: str = Field(..., min_length=2, max_length=150)
    bio: str = Field(..., min_length=5, max_length=1500)
    hourly_rate: float = Field(..., gt=0, le=10000)


def require_admin(
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


def user_payload(user, mentor=None):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "mentor": {
            "id": mentor.id,
            "name": mentor.name,
            "expertise": mentor.expertise,
            "bio": mentor.bio,
            "hourly_rate": mentor.hourly_rate,
        } if mentor else None
    }


@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    users = (
        db.query(models.User)
        .order_by(models.User.id.desc())
        .all()
    )

    mentor_profiles = {
        mentor.owner_id: mentor
        for mentor in db.query(models.Mentor).all()
    }

    return [
        user_payload(user, mentor_profiles.get(user.id))
        for user in users
    ]


@router.post("/users/{user_id}/make-mentor")
def make_user_mentor(
    user_id: int,
    payload: MakeMentorRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Admin account cannot be converted to mentor"
        )

    mentor = (
        db.query(models.Mentor)
        .filter(models.Mentor.owner_id == user.id)
        .first()
    )

    if mentor is None:
        mentor = models.Mentor(
            owner_id=user.id,
            name=user.full_name,
            expertise=payload.expertise.strip(),
            bio=payload.bio.strip(),
            hourly_rate=payload.hourly_rate
        )

        db.add(mentor)
    else:
        mentor.name = user.full_name
        mentor.expertise = payload.expertise.strip()
        mentor.bio = payload.bio.strip()
        mentor.hourly_rate = payload.hourly_rate

    user.role = "mentor"

    db.commit()
    db.refresh(user)
    db.refresh(mentor)

    return {
        "message": "User successfully converted to mentor",
        "user": user_payload(user, mentor)
    }


@router.put("/users/{user_id}/make-user")
def remove_mentor_role(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Admin role cannot be removed"
        )

    mentor = (
        db.query(models.Mentor)
        .filter(models.Mentor.owner_id == user.id)
        .first()
    )

    if mentor:
        mentor_booking_count = (
            db.query(models.Booking)
            .filter(models.Booking.mentor_id == mentor.id)
            .count()
        )

        mentor_review_count = (
            db.query(models.Review)
            .filter(models.Review.mentor_id == mentor.id)
            .count()
        )

        if mentor_booking_count or mentor_review_count:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Mentorun görüşləri və ya rəyləri var. "
                    "Mentor rolu silinə bilməz."
                )
            )

        db.delete(mentor)

    user.role = "user"

    db.commit()
    db.refresh(user)

    return {
        "message": "Mentor role removed",
        "user": user_payload(user)
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == admin.id:
        raise HTTPException(
            status_code=400,
            detail="Öz admin hesabınızı silə bilməzsiniz."
        )

    if user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Admin hesabı bu paneldən silinə bilməz."
        )

    user_booking_count = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == user.id)
        .count()
    )

    user_review_count = (
        db.query(models.Review)
        .filter(models.Review.user_id == user.id)
        .count()
    )

    mentor = (
        db.query(models.Mentor)
        .filter(models.Mentor.owner_id == user.id)
        .first()
    )

    mentor_booking_count = 0
    mentor_review_count = 0

    if mentor:
        mentor_booking_count = (
            db.query(models.Booking)
            .filter(models.Booking.mentor_id == mentor.id)
            .count()
        )

        mentor_review_count = (
            db.query(models.Review)
            .filter(models.Review.mentor_id == mentor.id)
            .count()
        )

    if (
        user_booking_count
        or user_review_count
        or mentor_booking_count
        or mentor_review_count
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Bu hesabın görüşləri və ya rəyləri var. "
                "Məlumat itkisinə görə hesab silinə bilməz."
            )
        )

    if mentor:
        db.delete(mentor)
        db.flush()

    db.delete(user)
    db.commit()

    return {
        "message": "İstifadəçi uğurla silindi."
    }

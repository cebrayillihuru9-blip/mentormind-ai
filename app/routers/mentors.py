from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db


router = APIRouter(
    prefix="/mentors",
    tags=["Mentors"]
)


def mentor_payload(
    mentor: models.Mentor,
    average_rating=None,
    reviews_count=0
):
    return {
        "id": mentor.id,
        "name": mentor.name,
        "expertise": mentor.expertise,
        "bio": mentor.bio,
        "hourly_rate": mentor.hourly_rate,
        "owner_id": mentor.owner_id,
        "average_rating": (
            round(float(average_rating), 2)
            if average_rating is not None
            else None
        ),
        "reviews_count": int(reviews_count or 0),
    }


@router.post(
    "/",
    response_model=schemas.MentorResponse,
    status_code=status.HTTP_201_CREATED
)
def create_mentor(
    mentor: schemas.MentorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing_profile = (
        db.query(models.Mentor)
        .filter(models.Mentor.owner_id == current_user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="You already have a mentor profile"
        )

    db_mentor = models.Mentor(
        name=mentor.name.strip(),
        expertise=mentor.expertise.strip(),
        bio=mentor.bio.strip(),
        hourly_rate=mentor.hourly_rate,
        owner_id=current_user.id
    )

    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)

    return mentor_payload(db_mentor)


@router.get(
    "/mine",
    response_model=schemas.MentorResponse
)
def get_my_mentor_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = (
        db.query(
            models.Mentor,
            func.avg(models.Review.rating),
            func.count(models.Review.id)
        )
        .outerjoin(
            models.Review,
            models.Mentor.id == models.Review.mentor_id
        )
        .filter(models.Mentor.owner_id == current_user.id)
        .group_by(models.Mentor.id)
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor profile not found"
        )

    mentor, average_rating, reviews_count = result

    return mentor_payload(
        mentor,
        average_rating,
        reviews_count
    )


@router.get(
    "/",
    response_model=list[schemas.MentorResponse]
)
def get_mentors(
    db: Session = Depends(get_db),
    name: str | None = None,
    expertise: str | None = None,
    min_rate: float | None = None,
    max_rate: float | None = None,
    skip: int = 0,
    limit: int = 50
):
    query = (
        db.query(
            models.Mentor,
            func.avg(models.Review.rating).label("average_rating"),
            func.count(models.Review.id).label("reviews_count")
        )
        .outerjoin(
            models.Review,
            models.Mentor.id == models.Review.mentor_id
        )
        .group_by(models.Mentor.id)
    )

    if name:
        query = query.filter(
            models.Mentor.name.ilike(f"%{name.strip()}%")
        )

    if expertise:
        query = query.filter(
            models.Mentor.expertise.ilike(
                f"%{expertise.strip()}%"
            )
        )

    if min_rate is not None:
        query = query.filter(
            models.Mentor.hourly_rate >= min_rate
        )

    if max_rate is not None:
        query = query.filter(
            models.Mentor.hourly_rate <= max_rate
        )

    results = (
        query
        .order_by(models.Mentor.id.desc())
        .offset(max(skip, 0))
        .limit(min(max(limit, 1), 100))
        .all()
    )

    return [
        mentor_payload(
            mentor,
            average_rating,
            reviews_count
        )
        for mentor, average_rating, reviews_count in results
    ]


@router.get(
    "/{mentor_id}",
    response_model=schemas.MentorResponse
)
def get_mentor(
    mentor_id: int,
    db: Session = Depends(get_db)
):
    result = (
        db.query(
            models.Mentor,
            func.avg(models.Review.rating),
            func.count(models.Review.id)
        )
        .outerjoin(
            models.Review,
            models.Mentor.id == models.Review.mentor_id
        )
        .filter(models.Mentor.id == mentor_id)
        .group_by(models.Mentor.id)
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )

    mentor, average_rating, reviews_count = result

    return mentor_payload(
        mentor,
        average_rating,
        reviews_count
    )


@router.put(
    "/{mentor_id}",
    response_model=schemas.MentorResponse
)
def update_mentor(
    mentor_id: int,
    mentor: schemas.MentorUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_mentor = (
        db.query(models.Mentor)
        .filter(models.Mentor.id == mentor_id)
        .first()
    )

    if db_mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )

    if db_mentor.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot update this mentor profile"
        )

    db_mentor.name = mentor.name.strip()
    db_mentor.expertise = mentor.expertise.strip()
    db_mentor.bio = mentor.bio.strip()
    db_mentor.hourly_rate = mentor.hourly_rate

    db.commit()
    db.refresh(db_mentor)

    return mentor_payload(db_mentor)


@router.delete("/{mentor_id}")
def delete_mentor(
    mentor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mentor = (
        db.query(models.Mentor)
        .filter(models.Mentor.id == mentor_id)
        .first()
    )

    if mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )

    if mentor.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this mentor profile"
        )

    related_bookings = (
        db.query(models.Booking)
        .filter(models.Booking.mentor_id == mentor.id)
        .count()
    )

    related_reviews = (
        db.query(models.Review)
        .filter(models.Review.mentor_id == mentor.id)
        .count()
    )

    if related_bookings or related_reviews:
        raise HTTPException(
            status_code=409,
            detail=(
                "Mentor profile has bookings or reviews "
                "and cannot be deleted"
            )
        )

    db.delete(mentor)
    db.commit()

    return {
        "message": "Mentor profile deleted successfully"
    }

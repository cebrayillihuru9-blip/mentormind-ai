from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


def review_payload(review: models.Review):
    return {
        "id": review.id,
        "mentor_id": review.mentor_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "mentor_name": (
            review.mentor.name if review.mentor else None
        ),
        "user_name": (
            review.user.full_name if review.user else None
        ),
    }


@router.post(
    "/",
    response_model=schemas.ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mentor = (
        db.query(models.Mentor)
        .filter(models.Mentor.id == review.mentor_id)
        .first()
    )

    if mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )

    completed_booking = (
        db.query(models.Booking)
        .filter(
            models.Booking.user_id == current_user.id,
            models.Booking.mentor_id == review.mentor_id,
            models.Booking.status == "completed"
        )
        .first()
    )

    if completed_booking is None:
        raise HTTPException(
            status_code=403,
            detail="You can review only after a completed meeting"
        )

    existing_review = (
        db.query(models.Review)
        .filter(
            models.Review.user_id == current_user.id,
            models.Review.mentor_id == review.mentor_id
        )
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=409,
            detail="You have already reviewed this mentor"
        )

    db_review = models.Review(
        mentor_id=review.mentor_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment.strip()
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return review_payload(db_review)


@router.get(
    "/",
    response_model=list[schemas.ReviewResponse]
)
def get_reviews(
    db: Session = Depends(get_db)
):
    reviews = (
        db.query(models.Review)
        .order_by(models.Review.id.desc())
        .all()
    )

    return [
        review_payload(review)
        for review in reviews
    ]


@router.get(
    "/my",
    response_model=list[schemas.ReviewResponse]
)
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    reviews = (
        db.query(models.Review)
        .filter(models.Review.user_id == current_user.id)
        .order_by(models.Review.id.desc())
        .all()
    )

    return [
        review_payload(review)
        for review in reviews
    ]


@router.get(
    "/mentor/{mentor_id}",
    response_model=list[schemas.ReviewResponse]
)
def get_mentor_reviews(
    mentor_id: int,
    db: Session = Depends(get_db)
):
    reviews = (
        db.query(models.Review)
        .filter(models.Review.mentor_id == mentor_id)
        .order_by(models.Review.id.desc())
        .all()
    )

    return [
        review_payload(review)
        for review in reviews
    ]


@router.get(
    "/{review_id}",
    response_model=schemas.ReviewResponse
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    review = (
        db.query(models.Review)
        .filter(models.Review.id == review_id)
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    return review_payload(review)


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    review = (
        db.query(models.Review)
        .filter(models.Review.id == review_id)
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this review"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully"
    }

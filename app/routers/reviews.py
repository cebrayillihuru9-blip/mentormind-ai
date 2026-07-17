from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.post("/", response_model=schemas.ReviewResponse)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mentor = db.query(models.Mentor).filter(
        models.Mentor.id == review.mentor_id
    ).first()

    if mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )

    db_review = models.Review(
        mentor_id=review.mentor_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return db_review


@router.get("/", response_model=list[schemas.ReviewResponse])
def get_reviews(db: Session = Depends(get_db)):
    return db.query(models.Review).all()


@router.get("/{review_id}", response_model=schemas.ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    review = db.query(models.Review).filter(
        models.Review.id == review_id
    ).first()

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    return review


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    review = db.query(models.Review).filter(
        models.Review.id == review_id
    ).first()

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this review"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully"
    }
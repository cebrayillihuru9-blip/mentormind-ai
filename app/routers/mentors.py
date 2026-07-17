from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user


router = APIRouter(
    prefix="/mentors",
    tags=["Mentors"]
)


@router.post("/", response_model=schemas.MentorResponse)
def create_mentor(
    mentor: schemas.MentorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_mentor = models.Mentor(
        name=mentor.name,
        expertise=mentor.expertise,
        bio=mentor.bio,
        hourly_rate=mentor.hourly_rate,
        owner_id=current_user.id
    )

    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)

    return db_mentor



@router.get("/", response_model=list[schemas.MentorResponse])
def get_mentors(
    db: Session = Depends(get_db),
    name: str | None = None,
    expertise: str | None = None,
    min_rate: float | None = None,
    max_rate: float | None = None,
    skip: int = 0,
    limit: int = 10
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
            models.Mentor.name.ilike(f"%{name}%")
        )


    if expertise:
        query = query.filter(
            models.Mentor.expertise.ilike(f"%{expertise}%")
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
        .offset(skip)
        .limit(limit)
        .all()
    )


    mentors = []

    for mentor, average_rating, reviews_count in results:

        mentors.append(
            {
                "id": mentor.id,
                "name": mentor.name,
                "expertise": mentor.expertise,
                "bio": mentor.bio,
                "hourly_rate": mentor.hourly_rate,
                "owner_id": mentor.owner_id,
                "average_rating": round(average_rating, 2)
                if average_rating else None,
                "reviews_count": reviews_count
            }
        )

    return mentors



@router.get("/{mentor_id}", response_model=schemas.MentorResponse)
def get_mentor(
    mentor_id: int,
    db: Session = Depends(get_db)
):

    mentor = db.query(models.Mentor).filter(
        models.Mentor.id == mentor_id
    ).first()


    if mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )


    return mentor



@router.put("/{mentor_id}", response_model=schemas.MentorResponse)
def update_mentor(
    mentor_id: int,
    mentor: schemas.MentorUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    db_mentor = db.query(models.Mentor).filter(
        models.Mentor.id == mentor_id
    ).first()


    if db_mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )


    if db_mentor.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this mentor"
        )


    db_mentor.name = mentor.name
    db_mentor.expertise = mentor.expertise
    db_mentor.bio = mentor.bio
    db_mentor.hourly_rate = mentor.hourly_rate


    db.commit()
    db.refresh(db_mentor)


    return db_mentor



@router.delete("/{mentor_id}")
def delete_mentor(
    mentor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    mentor = db.query(models.Mentor).filter(
        models.Mentor.id == mentor_id
    ).first()


    if mentor is None:
        raise HTTPException(
            status_code=404,
            detail="Mentor not found"
        )


    if mentor.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this mentor"
        )


    db.delete(mentor)
    db.commit()


    return {
        "message": "Mentor deleted successfully"
    }
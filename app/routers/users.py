from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import hash_password, verify_password
from app.auth import create_access_token, get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# REGISTER
@router.post("/register", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # email artıq varsa yoxla
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user



# USERS LIST
@router.get("/", response_model=list[schemas.UserResponse])
def get_users(
    db: Session = Depends(get_db)
):
    return db.query(models.User).all()



# LOGIN
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )


    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    access_token = create_access_token(
        data={
            "sub": str(db_user.id)
        }
    )


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



# CURRENT USER
@router.get("/me")
def get_me(
    current_user=Depends(get_current_user)
):
    return current_user
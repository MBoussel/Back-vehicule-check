from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_data = payload.model_dump()
    plain_password = user_data.pop("password")

    db_user = User(
        **user_data,
        password_hash=hash_password(plain_password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.desc()).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email is not None:
        existing_user = (
            db.query(User)
            .filter(User.email == payload.email, User.id != user_id)
            .first()
        )
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Email already exists")

    update_data = payload.model_dump(exclude_unset=True)

    if "password" in update_data:
        plain_password = update_data.pop("password")
        user.password_hash = hash_password(plain_password)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}
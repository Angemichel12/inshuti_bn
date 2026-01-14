from sqlalchemy.orm import Session
from app.users import models, schemas
from app.core.security import hash_password


def create_user(db: Session, user_data: schemas.UserCreate):
    hashed_password = hash_password(user_data.password)

    user = models.User(
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        gender=user_data.gender,
        birth_date=user_data.birth_date,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

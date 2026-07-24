from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


def get_user_by_email(
    db: Session,
    email: str,
) -> Optional[User]:
    statement = select(User).where(
        func.lower(User.email) == email.lower()
    )

    return db.scalar(statement)


def get_user_by_id(
    db: Session,
    user_id: UUID,
) -> Optional[User]:
    return db.get(User, user_id)


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    role: UserRole,
) -> User:
    user = User(
        email=email.lower(),
        password_hash=password_hash,
        role=role,
    )

    db.add(user)
    db.flush()

    return user

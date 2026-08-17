from getpass import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def main() -> None:

    email = input(
        "Admin email: "
    ).strip().lower()

    if not email:
        print("Email cannot be empty.")
        return

    password = getpass(
        "Admin password: "
    )

    confirm_password = getpass(
        "Confirm password: "
    )

    if password != confirm_password:
        print(
            "Passwords do not match."
        )
        return

    if len(password) < 8:
        print(
            "Password must contain "
            "at least 8 characters."
        )
        return

    db = SessionLocal()

    try:

        existing = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing:
            print(
                "A user with this email "
                "already exists."
            )
            return

        hashed_password = hash_password(
            password
        )

        admin = User(
            email=email,
            password_hash=hashed_password,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )

        db.add(admin)

        db.commit()

        db.refresh(admin)

        print(
            "Admin account "
            "created successfully."
        )

        print(
            f"Admin ID: {admin.id}"
        )

        print(
            f"Admin email: {admin.email}"
        )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()
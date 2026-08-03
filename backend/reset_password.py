from getpass import getpass

from sqlalchemy import func

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def main() -> None:
    email = input("Account email: ").strip().lower()
    new_password = getpass("New password: ")
    confirm_password = getpass("Confirm new password: ")

    if new_password != confirm_password:
        print("Passwords do not match.")
        return

    if len(new_password) < 8:
        print("Password must contain at least 8 characters.")
        return

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(func.lower(User.email) == email)
            .first()
        )

        if user is None:
            print(f"No user exists with email: {email}")
            return

        user.password_hash = hash_password(new_password)
        db.commit()

        print(f"Password successfully reset for {email}")

    except Exception as error:
        db.rollback()
        print(f"Password reset failed: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
from getpass import getpass

from sqlalchemy import select

from app.core.database import SessionLocal

from app.core.security import (
    hash_password,
)

from app.models.user import (
    User,
    UserRole,
)


def main():

    email = input(
        "Admin email: "
    ).strip().lower()


    password = getpass(
        "Admin password: "
    )


    confirm_password = getpass(
        "Confirm password: "
    )


    if (
        password
        != confirm_password
    ):

        print(
            "Passwords do not match."
        )

        return


    if (
        len(password)
        < 8
    ):

        print(
            "Password must contain "
            "at least 8 characters."
        )

        return


    db = SessionLocal()


    try:

        existing = db.scalar(
            select(User)
            .where(
                User.email
                == email
            )
        )


        if existing:

            print(
                "A user with this email "
                "already exists."
            )

            return


        admin = User(
            email=email,

            password_hash=(
                hash_password(
                    password
                )
            ),

            role=(
                UserRole.ADMIN
            ),

            is_active=True,

            is_verified=True,
        )


        db.add(
            admin
        )

        db.commit()


        print(
            "Admin account "
            "created successfully."
        )


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


if __name__ == "__main__":
    main()
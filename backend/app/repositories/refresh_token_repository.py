from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def create_refresh_token(
    db: Session,
    user_id,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(refresh_token)
    db.flush()

    return refresh_token


def get_refresh_token_by_hash(
    db: Session,
    token_hash: str,
) -> Optional[RefreshToken]:
    statement = select(RefreshToken).where(
        RefreshToken.token_hash == token_hash
    )

    return db.scalar(statement)


def revoke_refresh_token(
    refresh_token: RefreshToken,
) -> None:
    refresh_token.revoked_at = datetime.now(timezone.utc)

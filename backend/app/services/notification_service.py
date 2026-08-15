from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: UUID,
    notification_type: str,
    title: str,
    message: str,
    action_url: Optional[str] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[UUID] = None,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        is_read=False,
    )

    db.add(notification)

    return notification


def get_user_notifications(
    db: Session,
    user_id: UUID,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
):

    query = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id
        )
    )

    if unread_only:
        query = query.filter(
            Notification.is_read.is_(False)
        )

    return (
        query
        .order_by(
            Notification.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_unread_count(
    db: Session,
    user_id: UUID,
) -> int:

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .count()
    )


def mark_notification_as_read(
    db: Session,
    notification: Notification,
) -> Notification:

    notification.is_read = True

    notification.read_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: UUID,
) -> int:

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for notification in notifications:
        notification.is_read = True
        notification.read_at = now

    db.commit()

    return len(notifications)


def delete_notification(
    db: Session,
    notification: Notification,
) -> None:

    db.delete(notification)
    db.commit()
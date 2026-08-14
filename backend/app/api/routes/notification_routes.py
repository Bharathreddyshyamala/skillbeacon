from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session


from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
)
from app.services.notification_service import (
    delete_notification,
    get_unread_count,
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)

from app.core.database import get_db
from app.api.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

@router.get(
    "",
    response_model=NotificationListResponse,
)
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(
        50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    notifications = get_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )

    unread_count = get_unread_count(
        db=db,
        user_id=current_user.id,
    )

    return {
        "notifications": notifications,
        "unread_count": unread_count,
    }

@router.get(
    "/unread-count",
)
def unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    count = get_unread_count(
        db=db,
        user_id=current_user.id,
    )

    return {
        "unread_count": count,
    }

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def read_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id
            == notification_id,
            Notification.user_id
            == current_user.id,
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    if notification.is_read:
        return notification

    return mark_notification_as_read(
        db=db,
        notification=notification,
    )

@router.patch(
    "/read-all",
)
def read_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    updated_count = (
        mark_all_notifications_as_read(
            db=db,
            user_id=current_user.id,
        )
    )

    return {
        "updated_count": updated_count,
        "message": "Notifications marked as read.",
    }

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id
            == notification_id,
            Notification.user_id
            == current_user.id,
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    delete_notification(
        db=db,
        notification=notification,
    )
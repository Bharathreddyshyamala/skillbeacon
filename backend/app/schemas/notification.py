from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID

    notification_type: str

    title: str
    message: str

    action_url: Optional[str] = None

    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None

    is_read: bool

    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int
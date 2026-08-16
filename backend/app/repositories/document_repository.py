from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentType


def create_document(
    db: Session,
    user_id: UUID,
    document_type: DocumentType,
    storage_key: str,
    file_name: str,
    file_url: str,
    mime_type: str,
    size_bytes: int,
) -> Document:
    doc = Document(
        user_id=user_id,
        document_type=document_type,
        storage_key=storage_key,
        file_name=file_name,
        file_url=file_url,
        mime_type=mime_type,
        size_bytes=size_bytes,
        is_active=True,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document_by_id(
    db: Session,
    document_id: UUID,
) -> Optional[Document]:
    return db.query(Document).filter(
        Document.id == document_id,
        Document.is_active == True,
    ).first()


def get_user_documents(
    db: Session,
    user_id: UUID,
    document_type: Optional[DocumentType] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Document]:
    query = db.query(Document).filter(
        Document.user_id == user_id,
        Document.is_active == True,
    )
    if document_type:
        query = query.filter(Document.document_type == document_type)

    return query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()


def count_user_documents(
    db: Session,
    user_id: UUID,
    document_type: Optional[DocumentType] = None,
) -> int:
    query = db.query(func.count(Document.id)).filter(
        Document.user_id == user_id,
        Document.is_active == True,
    )
    if document_type:
        query = query.filter(Document.document_type == document_type)
    return int(query.scalar() or 0)


def get_user_storage_usage(
    db: Session,
    user_id: UUID,
) -> int:
    """
    Returns the total cumulative storage usage in bytes for a user.
    """
    total = db.query(func.coalesce(func.sum(Document.size_bytes), 0)).filter(
        Document.user_id == user_id,
        Document.is_active == True,
    ).scalar()
    return int(total or 0)


def get_active_resumes_for_user(
    db: Session,
    user_id: UUID,
) -> List[Document]:
    return db.query(Document).filter(
        Document.user_id == user_id,
        Document.document_type == DocumentType.RESUME,
        Document.is_active == True,
    ).all()


def get_active_logos_for_user(
    db: Session,
    user_id: UUID,
) -> List[Document]:
    return db.query(Document).filter(
        Document.user_id == user_id,
        Document.document_type == DocumentType.EMPLOYER_LOGO,
        Document.is_active == True,
    ).all()


def delete_document_record(
    db: Session,
    document: Document,
) -> None:
    db.delete(document)
    db.commit()

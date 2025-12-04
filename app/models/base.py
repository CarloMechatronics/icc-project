from datetime import datetime
from app import db


class TimestampMixin:
    """Adds created_at and updated_at columns to a model."""

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

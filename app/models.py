import uuid
import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    ForeignKey,
    DateTime,
    JSON,
    UniqueConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, processing, processed, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    metadata_rel = relationship(
        "ImageMetadata",
        back_populates="image",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    matches = relationship(
        "Match",
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    cost_logs = relationship(
        "AICostLog",
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ImageMetadata(Base):
    __tablename__ = "image_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(
        UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    subject = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    attributes = Column(JSON, default=list, nullable=False)
    caption = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Back-reference
    image = relationship("Image", back_populates="metadata_rel")


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    matches = relationship(
        "Match",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    cost_logs = relationship(
        "AICostLog",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_id = Column(
        UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    similarity_score = Column(Float, nullable=False)
    status = Column(
        String, nullable=False, default="suggested"
    )  # suggested, approved, rejected, guarded_mismatch
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Back-references
    post = relationship("Post", back_populates="matches")
    image = relationship("Image", back_populates="matches")

    # Composite uniqueness constraint
    __table_args__ = (
        UniqueConstraint("post_id", "image_id", name="uq_post_image_match"),
    )


class AICostLog(Base):
    __tablename__ = "ai_cost_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String, nullable=False)  # vision, embedding
    model = Column(String, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    estimated_cost = Column(Float, default=0.0, nullable=False)
    
    # Optional direct attribution to the resource processed
    image_id = Column(
        UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="CASCADE"),
        nullable=True,
    )
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Back-references
    image = relationship("Image", back_populates="cost_logs")
    post = relationship("Post", back_populates="cost_logs")
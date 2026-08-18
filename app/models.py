from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
import datetime
from .database import Base

class Image(Base):
    __tablename__ = "images"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, unique=True, index=True)
    status = Column(String, default="pending") # pending, processed, failed
    
class ImageMetadata(Base):
    __tablename__ = "image_metadata"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"))
    subject = Column(String)
    category = Column(String)
    attributes = Column(JSON)
    caption = Column(String)
    confidence = Column(Float)
    embedding = Column(Vector(768)) # Gemini uses 768 dimensions for embeddings

class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    content = Column(String)
    embedding = Column(Vector(768))

class Match(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"))
    similarity_score = Column(Float)
    status = Column(String) # suggested, approved, rejected, guarded_mismatch
    rejection_reason = Column(String, nullable=True)

class AICostLog(Base):
    __tablename__ = "ai_cost_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String) # vision, embedding
    model = Column(String)
    tokens_used = Column(Integer)
    estimated_cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
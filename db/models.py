import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Room(Base):
    __tablename__ = "rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationship to files
    files = relationship("File", back_populates="room", cascade="all, delete-orphan")
    executions = relationship("CodeExecution", back_populates="room", cascade="all, delete-orphan")
    users = relationship("User", back_populates="room", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_online = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    room = relationship("Room", back_populates="users")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text, default="")
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    room = relationship("Room", back_populates="files")

class CodeExecution(Base):
    __tablename__ = "code_executions"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    code = Column(Text)
    output = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="executions")
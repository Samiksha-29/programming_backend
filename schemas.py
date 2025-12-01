from pydantic import BaseModel
import uuid

class RoomBase(BaseModel):
    content: str

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class RoomInfo(BaseModel):
    roomId: str

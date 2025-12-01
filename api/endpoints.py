from io import StringIO
import sys
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
from datetime import datetime

from db.database import SessionLocal
from db import models
from schemas import RoomCreate, Room, RoomInfo
from pydantic import BaseModel

app = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Dict]] = {}  # room_id -> list of {websocket, user_id}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append({"websocket": websocket, "user_id": user_id})
        
        # Broadcast updated user list
        await self.broadcast({
            "type": "users",
            "users": self.get_active_users(room_id)
        }, room_id, sender=None)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            user_id = None
            for conn in self.active_connections[room_id]:
                if conn["websocket"] == websocket:
                    user_id = conn["user_id"]
                    self.active_connections[room_id].remove(conn)
                    break
            return user_id
        return None

    async def broadcast(self, message: dict, room_id: str, sender: WebSocket = None):
        if room_id in self.active_connections:
            for conn in self.active_connections[room_id]:
                if sender is None or conn["websocket"] != sender:
                    try:
                        await conn["websocket"].send_json(message)
                    except:
                        pass  # Connection might be closed
    
    def get_active_users(self, room_id: str) -> List[str]:
        if room_id in self.active_connections:
            return [conn["user_id"] for conn in self.active_connections[room_id]]
        return []
    
    def get_user_count(self, room_id: str) -> int:
        return len(self.active_connections.get(room_id, []))

manager = ConnectionManager()


# --- Pydantic Models ---
class FileCreate(BaseModel):
    filename: str
    roomId: str

class FileUpdate(BaseModel):
    content: str

class RunCodeRequest(BaseModel):
    code: str

# --- API ENDPOINTS ---

@app.post("/rooms")
async def create_room(db: Session = Depends(get_db)):
    import uuid
    room_id = str(uuid.uuid4())
    db_room = models.Room(id=room_id)
    db.add(db_room)
    
    # Create a default file
    default_file = models.File(filename="main.py", content="# Welcome to Pair Programming!\n# Start coding together...\n\nprint('Hello World')", room_id=room_id)
    db.add(default_file)
    
    db.commit()
    return {"roomId": room_id}

@app.get("/rooms/{room_id}")
async def get_room(room_id: str, db: Session = Depends(get_db)):
    room_id = room_id.strip()  # Remove any whitespace
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return {
        "roomId": str(db_room.id),
        "createdAt": db_room.created_at.isoformat(),
        "activeUsers": manager.get_user_count(room_id),
        "fileCount": len(db_room.files)
    }

@app.get("/rooms/{room_id}/files")
async def get_files(room_id: str, db: Session = Depends(get_db)):
    room_id = room_id.strip()  # Remove any whitespace
    files = db.query(models.File).filter(models.File.room_id == room_id).all()
    return files

@app.post("/files")
async def create_file(file: FileCreate, db: Session = Depends(get_db)):
    db_file = models.File(filename=file.filename, content="", room_id=file.roomId)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

@app.put("/files/{file_id}")
async def save_file(file_id: int, file: FileUpdate, db: Session = Depends(get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file: raise HTTPException(status_code=404, detail="File not found")
    db_file.content = file.content
    db.commit()
    return {"status": "saved"}

@app.delete("/files/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(db_file)
    db.commit()
    return {"status": "deleted"}

@app.get("/rooms/{room_id}/active-users")
async def get_active_users(room_id: str):
    room_id = room_id.strip()  # Remove any whitespace
    return {
        "roomId": room_id,
        "activeUsers": manager.get_active_users(room_id),
        "count": manager.get_user_count(room_id)
    }

@app.post("/run")
async def run_code(req: RunCodeRequest, db: Session = Depends(get_db)):
    # WARNING: unsafe, use only for prototype
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    output = ""
    error = None
    
    try:
        exec(req.code)
        output = redirected_output.getvalue()
    except Exception as e:
        output = f"Error: {str(e)}"
        error = str(e)
    finally:
        sys.stdout = old_stdout
    
    return {"output": output, "error": error}

@app.post("/rooms/{room_id}/execute")
async def execute_code(room_id: str, req: RunCodeRequest, db: Session = Depends(get_db)):
    room_id = room_id.strip()  # Remove any whitespace
    # Verify room exists
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Execute code
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    output = ""
    
    try:
        exec(req.code)
        output = redirected_output.getvalue()
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        sys.stdout = old_stdout
    
    # Store execution history
    execution = models.CodeExecution(
        room_id=room_id,
        code=req.code,
        output=output
    )
    db.add(execution)
    db.commit()
    
    return {"output": output, "executionId": execution.id}

@app.get("/rooms/{room_id}/executions")
async def get_executions(room_id: str, limit: int = 10, db: Session = Depends(get_db)):
    room_id = room_id.strip()  # Remove any whitespace
    executions = db.query(models.CodeExecution)\
        .filter(models.CodeExecution.room_id == room_id)\
        .order_by(models.CodeExecution.executed_at.desc())\
        .limit(limit)\
        .all()
    
    return [{
        "id": ex.id,
        "code": ex.code,
        "output": ex.output,
        "executedAt": ex.executed_at.isoformat()
    } for ex in executions]

@app.post("/autocomplete")
async def autocomplete(payload: Dict):
    code = payload.get("code", "")
    cursor_position = payload.get("cursorPosition", 0)
    
    # Get text before cursor
    text_before_cursor = code[:cursor_position]
    text_after_cursor = code[cursor_position:]
    
    # Get the current line
    lines_before = text_before_cursor.split('\n')
    current_line = lines_before[-1] if lines_before else ""
    
    # Get the last word being typed
    current_line_stripped = current_line.strip()
    words = current_line_stripped.split()
    last_word = words[-1] if words else ""
    
    print(f"Current line: '{current_line}'")
    print(f"Last word: '{last_word}'")
    print(f"Cursor position: {cursor_position}")
    
    # Simple rule-based autocomplete suggestions
    suggestion = ""
    
    # Check what's being typed
    if not current_line_stripped:
        # Empty line - suggest common Python statements
        suggestion = "def main():"
    
    # Import suggestions
    elif current_line_stripped == "import" or current_line_stripped.endswith("import"):
        suggestion = " os"
    elif current_line_stripped.startswith("import") and last_word == "import":
        suggestion = " os"
    elif current_line_stripped == "from" or current_line_stripped.endswith("from"):
        suggestion = " os import"
    
    # Function definition
    elif current_line_stripped == "def":
        suggestion = " main():"
    elif current_line_stripped.startswith("def") and "(" not in current_line:
        suggestion = "():"
    elif current_line_stripped.startswith("def") and "(" in current_line and ")" not in current_line:
        suggestion = "):"
    elif current_line_stripped.startswith("def") and ")" in current_line and ":" not in current_line:
        suggestion = ":"
    
    # Class definition
    elif current_line_stripped == "class":
        suggestion = " MyClass:"
    elif current_line_stripped.startswith("class") and ":" not in current_line:
        suggestion = ":"
    
    # Print function
    elif current_line_stripped == "print":
        suggestion = "()"
    elif "print(" in current_line_stripped and '"' in current_line and current_line.count('"') == 1:
        # Inside a string in print statement
        suggestion = '")'
    elif "print(" in current_line_stripped and ")" not in current_line:
        suggestion = ')'
    
    # Return statement
    elif current_line_stripped == "return":
        suggestion = ' "Hello, World!"'
    elif current_line_stripped.startswith("return") and '"' in current_line and current_line.count('"') == 1:
        # Closing the string
        suggestion = '"'
    
    # If statement
    elif current_line_stripped == "if":
        suggestion = " True:"
    elif current_line_stripped.startswith("if") and ":" not in current_line:
        suggestion = ":"
    
    # For loop
    elif current_line_stripped == "for":
        suggestion = " i in range(10):"
    elif current_line_stripped.startswith("for") and " in " not in current_line:
        suggestion = " in range(10):"
    elif current_line_stripped.startswith("for") and " in " in current_line and ":" not in current_line:
        suggestion = ":"
    
    # While loop
    elif current_line_stripped == "while":
        suggestion = " True:"
    elif current_line_stripped.startswith("while") and ":" not in current_line:
        suggestion = ":"
    
    # Partial word matching
    elif last_word:
        if last_word == "d" or last_word == "de":
            suggestion = "def main():"[len(last_word):]
        elif last_word == "pri" or last_word == "prin":
            suggestion = "print()"[len(last_word):]
        elif last_word == "imp" or last_word == "impo" or last_word == "impor":
            suggestion = "import"[len(last_word):] + " os"
        elif last_word == "cla" or last_word == "clas":
            suggestion = "class"[len(last_word):] + " MyClass:"
        elif last_word == "fo":
            suggestion = "r i in range(10):"
        elif last_word == "ret" or last_word == "retu" or last_word == "retur":
            suggestion = "return"[len(last_word):] + " True"
    
    print(f"Suggestion: '{suggestion}'")
    return {"suggestion": suggestion}


@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = "Anonymous", db: Session = Depends(get_db)):
    room_id = room_id.strip()  # Remove any whitespace
    username = username.strip() if username else "Anonymous"
    
    # Generate user_id
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # Store user in database
    db_user = models.User(username=username, room_id=room_id, is_online=True)
    db.add(db_user)
    db.commit()
    
    await manager.connect(websocket, room_id, username)
    
    try:
        while True:
            # Expecting JSON: { "type": "code"|"cursor"|"chat", "fileId": 1, "data": ... }
            data = await websocket.receive_json()
            
            # Add sender info (use username, not user_id)
            data["senderId"] = username
            data["timestamp"] = datetime.utcnow().isoformat()
            
            await manager.broadcast(data, room_id, sender=websocket)
    except WebSocketDisconnect:
        username = manager.disconnect(websocket, room_id)
        if username:
            # Mark user as offline in database
            db_user = db.query(models.User).filter(
                models.User.username == username,
                models.User.room_id == room_id
            ).first()
            if db_user:
                db_user.is_online = False
                db.commit()
            
            # Notify others with updated user list
            await manager.broadcast({
                "type": "users",
                "users": manager.get_active_users(room_id)
            }, room_id, sender=None)

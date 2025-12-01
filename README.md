# Real-Time Collaborative Code Editor - Backend

A powerful FastAPI-based backend for real-time collaborative code editing with WebSocket support, code execution, and PostgreSQL database integration.

## 🔗 Links

- **Frontend Repository:** (https://github.com/Samiksha-29/programming_backend/)
- **Live Demo:** (https://drive.google.com/file/d/1I6JugoB_wole--ySCJj6jVbc8WQt6U28/view?usp=sharing)

## ✨ Features

- **Real-time Collaboration:** WebSocket-based synchronization for multiple users
- **Code Execution:** Execute Python code with instant output
- **File Management:** Create, update, delete, and organize files per room
- **Version History:** Track and restore previous code versions
- **User Management:** Track online users and their activities
- **RESTful API:** Comprehensive REST endpoints for all operations
- **Database Persistence:** PostgreSQL for reliable data storage

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **WebSocket:** FastAPI WebSockets
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **CORS:** FastAPI CORS Middleware
- **Code Execution:** Python subprocess

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone [repository-url]
cd [repository-name]
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

Or copy from example:

```bash
copy .env.example .env
```

### 5. Configure Database

Update `config.py` with your PostgreSQL credentials if not using `.env`:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/database_name"
```

### 6. Initialize Database

The database tables will be created automatically on first run, or you can initialize manually:

```bash
python -c "from db.database import engine; from db.models import Base; Base.metadata.create_all(bind=engine)"
```

### 7. Start the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📚 API Documentation

Interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI)

### REST Endpoints

#### Rooms

**POST /rooms**
- Create a new collaboration room
- Response: `{ "room_id": "uuid" }`

**GET /rooms/{room_id}**
- Get room information
- Response: Room details and metadata

**GET /rooms/{room_id}/files**
- Get all files in a room
- Response: Array of file objects

#### Files

**POST /files**
- Create a new file
- Request Body: `{ "filename": "string", "roomId": "uuid" }`
- Response: File object

**PUT /files/{file_id}**
- Update file content
- Request Body: `{ "content": "string" }`
- Response: Success status

**DELETE /files/{file_id}**
- Delete a file
- Response: Success status

#### Code Execution

**POST /run**
- Execute Python code
- Request Body: `{ "code": "string" }`
- Response: `{ "output": "string", "error": "string" }`

### WebSocket API

**Connection URL:** `ws://localhost:8000/ws/rooms/{room_id}?username={username}`

#### Message Types

**Code Update:**
```json
{
  "type": "code",
  "fileId": 1,
  "data": "code content",
  "senderId": "username"
}
```

**Cursor Position:**
```json
{
  "type": "cursor",
  "fileId": 1,
  "position": {
    "lineNumber": 1,
    "column": 1
  },
  "senderId": "username"
}
```

**User List:**
```json
{
  "type": "users",
  "users": ["Alice", "Bob"]
}
```

**User Join/Leave:**
```json
{
  "type": "user_joined",
  "username": "Alice"
}
```

## 🗄️ Database Schema

### Tables

#### rooms
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary Key |
| created_at | Timestamp | Room creation time |

#### users
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| username | String | User display name |
| room_id | UUID | Foreign Key to rooms |
| joined_at | Timestamp | Join timestamp |
| is_online | Boolean | Online status |
| last_seen | Timestamp | Last activity time |

#### files
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| filename | String | File name |
| content | Text | File content |
| room_id | UUID | Foreign Key to rooms |
| created_at | Timestamp | Creation time |
| updated_at | Timestamp | Last update time |

#### code_executions
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| room_id | UUID | Foreign Key to rooms |
| code | Text | Executed code |
| output | Text | Execution output |
| executed_at | Timestamp | Execution time |

## 🧪 Testing

Run the test suite:

```bash
pytest test_api.py
```

Or test specific endpoints:

```bash
pytest test_api.py::test_create_room
```

## 🚢 Deployment

### Production Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔒 Security

- **Input Validation:** Pydantic schemas validate all inputs
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries
- **CORS Configuration:** Configurable for production environments
- **WebSocket Authentication:** Username-based authentication
- **Code Execution Sandboxing:** Limited Python execution environment

## ⚡ Performance
- WebSocket connection pooling per room
- Database query optimization with proper indexing
- Async/await for non-blocking operations
- Connection management for PostgreSQL

##  Troubleshooting

### Cannot connect to database
- Verify PostgreSQL is running
- Check database credentials in `.env` or `config.py`
- Ensure database exists: `createdb database_name`

### WebSocket connection fails
- Check firewall settings for port 8000
- Verify WebSocket URL format: `ws://localhost:8000/ws/rooms/{room_id}?username={name}`
- Ensure room ID is valid

### Code execution fails
- Verify Python syntax
- Check backend logs for detailed errors
- Ensure subprocess execution is allowed

### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📁 Project Structure

```
.
├── api/
│   └── endpoints.py          # API route handlers
├── db/
│   ├── database.py           # Database connection
│   └── models.py             # SQLAlchemy models
├── main.py                   # Application entry point
├── config.py                 # Configuration settings
├── schemas.py                # Pydantic schemas
├── requirements.txt          # Python dependencies
├── test_api.py              # API tests
├── .env.example             # Environment variables template
└── README.md                # Documentation
```

## 🔮 Future Enhancements

- [ ] Support for multiple programming languages (JavaScript, Java, C++)
- [ ] Enhanced code execution with timeout and resource limits
- [ ] File upload/download functionality
- [ ] Code syntax highlighting and linting
- [ ] User authentication and authorization
- [ ] Room access control and permissions
- [ ] Chat messaging system
- [ ] Code review and commenting features
- [ ] Git integration
- [ ] Collaborative debugging tools


## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [PostgreSQL](https://www.postgresql.org/) - Database system
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import app as api_router
from db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the real-time pair-programming API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/rooms/{room_id}"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

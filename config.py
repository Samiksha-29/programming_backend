"""
Configuration settings for the application
"""
import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://dummy_owner:dummy_pass@dummy.aws.neon.tech/neondb"
    )
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
    
    # Code Execution
    CODE_EXECUTION_TIMEOUT: int = int(os.getenv("CODE_EXECUTION_TIMEOUT", "5"))
    MAX_OUTPUT_LENGTH: int = int(os.getenv("MAX_OUTPUT_LENGTH", "10000"))
    
    # Room Settings
    MAX_FILES_PER_ROOM: int = int(os.getenv("MAX_FILES_PER_ROOM", "50"))
    MAX_USERS_PER_ROOM: int = int(os.getenv("MAX_USERS_PER_ROOM", "10"))
    
    # Autocomplete
    AUTOCOMPLETE_DEBOUNCE_MS: int = int(os.getenv("AUTOCOMPLETE_DEBOUNCE_MS", "600"))

settings = Settings()

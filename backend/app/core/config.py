import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    AI_ENABLED = True  
    

    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    

    MAX_FILE_SIZE = 5 * 1024 * 1024  
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}

settings = Settings()
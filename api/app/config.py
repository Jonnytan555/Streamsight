import os
from dotenv import load_dotenv

load_dotenv()

APP_BASE_URL        = os.getenv("APP_BASE_URL", "http://localhost:5173")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "cnt_session")

JWT_SECRET_KEY   = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM    = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "8"))

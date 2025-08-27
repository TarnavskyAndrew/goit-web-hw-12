import os
from dotenv import load_dotenv


load_dotenv()

class Config:

    # DB
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL must be set in .env")

    @property
    def SYNC_DATABASE_URL(self):
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")  # type: ignore


    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in .env")

    ALGORITHM = "HS256"

    ACCESS_EXPIRE_MIN = os.getenv("ACCESS_EXPIRE_MIN")
    if not ACCESS_EXPIRE_MIN:
        raise ValueError("ACCESS_EXPIRE_MIN must be set in .env")
    ACCESS_EXPIRE_MIN = int(ACCESS_EXPIRE_MIN)

    REFRESH_EXPIRE_DAYS = os.getenv("REFRESH_EXPIRE_DAYS")
    if not REFRESH_EXPIRE_DAYS:
        raise ValueError("REFRESH_EXPIRE_DAYS must be set in .env")
    REFRESH_EXPIRE_DAYS = int(REFRESH_EXPIRE_DAYS)


    # Admin for seed.py
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    if not ADMIN_EMAIL:
        raise ValueError("ADMIN_EMAIL must be set in .env")

    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    if not ADMIN_PASSWORD:
        raise ValueError("ADMIN_PASSWORD must be set in .env")


config = Config()

# shortcuts
DATABASE_URL = config.DATABASE_URL
SYNC_DATABASE_URL = config.SYNC_DATABASE_URL
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_EXPIRE_MIN = config.ACCESS_EXPIRE_MIN
REFRESH_EXPIRE_DAYS = config.REFRESH_EXPIRE_DAYS
ADMIN_EMAIL = config.ADMIN_EMAIL
ADMIN_PASSWORD = config.ADMIN_PASSWORD

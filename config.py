import os

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    
settings = Settings()
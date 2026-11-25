from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import Base
from routers import books, users

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
            title="FastAPI Books API",
            description="Учебный проект с JWT-авторизацией, PostgreSQL и миграциями",
            version="1.0.0",
            )

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Подключаем роутеры
app.include_router(books.router)
app.include_router(users.router)
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# Описываем таблицу books как класс Book
class Book(Base):
    __tablename__ = "books" # имя таблицы в БД
    
    # Описываем столбцы (колонки)
    id = Column(Integer, primary_key=True, index=True)  # первичный ключ
    title = Column(String, index=True)                  # название
    author = Column(String, index=True)                 # автор
    year = Column(Integer)                              # год
    is_published = Column(Boolean, default=False)       # опубликована ли
    
    # Связь с пользователем (внешний ключ)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Позволяет обращаться к создателю книги: book.owner.username
    owner = relationship("User", back_populates="books")
    
# Описываем таблицу users как класс User
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Связь с книгами
    books = relationship("Book", back_populates="owner")
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Book, User
from routers.users import get_current_user
from schemas import BookCreate, BookResponse

# Создаём роутер для книг
router = APIRouter(
    prefix="/books",
    tags=["books"]
)

# Просмотр всех книг
@router.get("/", response_model=list[BookResponse])
async def get_books(db: Session = Depends(get_db)):  # noqa: B008
    books = db.query(Book).all()
    return books

# Просмотр книги по ID
@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):  # noqa: B008
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book

# Создание книги (только зарегестрированный пользователь)
@router.post("/", response_model=BookResponse)
async def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user)  # noqa: B008
): 
    db_book = Book(
        title=book.title,
        author=book.author,
        year=book.year,
        user_id=current_user.id # <- Привязываем к текущему пользователю
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# Обновление книги (только автор)
@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book: BookCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user)  # noqa: B008
):  
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    # ПРОВЕРКА: Если книгу пытается обновить НЕ её автор
    if db_book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не можете редактировать чужую книгу")
    
    # Обновляем поля
    db_book.title = book.title
    db_book.author = book.author
    db_book.year = book.year
    
    db.commit()
    db.refresh(db_book)
    return db_book

# Удаление книги (только автор)
@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user)  # noqa: B008
): 
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    # ПРОВЕРКА: Если книгу пытается удалить НЕ её автор
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не можете удалить чужую книгу")
    
    db.delete(book)
    db.commit()
    return {"message": f"Книга с ID {book_id} удалена"}
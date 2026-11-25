from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from database import get_db
from models import User
from schemas import Token, UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# Это строка говорит FastAPI, что мы будем искать токен в заголовке Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Зависимость для получения текущего пользователя
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):  # noqa: B008
    # 1. Декодируем токен
    payload = decode_access_token(token)

    # 2. Если токен невалидный
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )

    # 3. Достаём username из поля "sub"
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Неверный токен")

    # 4. Ищем пользователя в базе
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    # 5. Возвращаем пользователя
    return user

# 1. Эндпоинт регистрации
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    # Проверяем, есть ли уже такой пользователь
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким именем уже существует")
    
    # Хешируем пароль
    hashed_pwd = get_password_hash(user_data.password)
    
    # Создаём нового пользователя
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# 2. Эндпоинт логина
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):  # noqa: B008
    # Ищем пользователя по имени
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Если пользователя нет ИЛИ пароль не совпадает
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
        
    # Создаём токен (в поле "sub" кладём имя пользователя)
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

# 3. Эндпоинт для получения профиля текущего пользователя
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):  # noqa: B008
    # FastAPI сначала проверит токен через get_current_user.
    # Если токен валидный, то в current_user будет лежать объек пользователя из БД.
    # Мы просто возвращаем его.
    return current_user
from pydantic import BaseModel, EmailStr


# Pydantic-модель для создания книги
class BookCreate(BaseModel):
    title: str
    author: str
    year: int

# Pydantic-модель для ответа
class BookResponse(BaseModel):
    title: str
    author: str
    year: int
    id: int
    
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True 

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
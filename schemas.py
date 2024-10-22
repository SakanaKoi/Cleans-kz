from pydantic import BaseModel
from typing import Optional
from models import UserRole


# Схемы для пользователя
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole

    class Config:
        orm_mode = True


# Схемы для продукта
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    available: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    available: int

    class Config:
        orm_mode = True


# Схемы для элемента корзины
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int

    class Config:
        orm_mode = True


# Схемы для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

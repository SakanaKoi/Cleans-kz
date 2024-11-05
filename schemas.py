from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from models import UserRole


# Схемы для пользователя
class UserBase(BaseModel):
    username: str = Field(..., description="Имя пользователя", example="john_doe")
    email: EmailStr = Field(..., description="Email пользователя", example="john@example.com")


class UserCreate(UserBase):
    password: str = Field(..., description="Пароль пользователя", example="1223456")


class UserResponse(UserBase):
    id: int = Field(..., description="ID пользователя", example=1)
    role: UserRole = Field(..., description="Роль пользователя", example="client")

    class Config:
        orm_mode = True


# Схемы для продукта
class ProductBase(BaseModel):
    name: str = Field(..., description="Название продукта", example="Чистка кожаной обуви")
    description: Optional[str] = Field(None, description="Описание продукта",
                                       example="Профессиональная чистка кожаной обуви")
    price: float = Field(..., description="Цена продукта", example=49.99)
    category: Optional[str] = Field(None, description="Категория продукта", example="Чистка")
    image_url: Optional[str] = Field(None, description="URL изображения продукта",
                                     example="http://example.com/images/cleaning.jpg")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    available: Optional[int] = Field(None, description="Доступность продукта (1 - доступен, 0 - недоступен)", example=1)


class ProductResponse(ProductBase):
    id: int = Field(..., description="ID продукта", example=1)
    available: int = Field(..., description="Доступность продукта (1 - доступен, 0 - недоступен)", example=1)

    class Config:
        orm_mode = True


# Схемы для элемента корзины
class CartItemCreate(BaseModel):
    product_id: int = Field(..., description="ID продукта", example=1)
    quantity: int = Field(..., description="Количество товара", example=2)


class CartItemResponse(BaseModel):
    id: int = Field(..., description="ID элемента корзины", example=1)
    product_id: int = Field(..., description="ID продукта", example=1)
    product_name: str = Field(..., description="Название продукта", example="Чистка кожаной обуви")
    product_price: float = Field(..., description="Цена продукта", example=49.99)
    quantity: int = Field(..., description="Количество товара", example=2)

    class Config:
        orm_mode = True


# Схемы для аутентификации
class Token(BaseModel):
    access_token: str = Field(..., description="Токен доступа", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., description="Тип токена", example="bearer")


class TokenData(BaseModel):
    username: Optional[str] = None

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(enum.Enum):
    client = "client"
    admin = "admin"


# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.client, nullable=False)
    is_active = Column(Integer, default=1)  # 1 - активен, 0 - неактивен

    cart_items = relationship("CartItem", back_populates="user")


# Модель товара
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    image_url = Column(String(255), nullable=True)
    available = Column(Integer, default=1)  # 1 - доступен, 0 - недоступен

    cart_items = relationship("CartItem", back_populates="product")


# Модель элемента корзины
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

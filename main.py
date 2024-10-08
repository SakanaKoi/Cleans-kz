from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, engine
from models import Base, Product, CartItem
from pydantic import BaseModel

# Создание таблиц в базе данных (если они не созданы)
Base.metadata.create_all(bind=engine)

app = FastAPI()


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int


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


# Главная страница
@app.get("/")
async def get_main_page():
    return {"message": "Добро пожаловать в интернет-магазин!"}


# Получение всех товаров в корзине
@app.get("/cart", response_model=List[CartItemResponse])
def get_cart(db: Session = Depends(get_db)):
    cart_items = db.query(CartItem).all()
    return [
        CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            product_price=item.product.price,
            quantity=item.quantity,
        )
        for item in cart_items
    ]


# Добавление товара в корзину
@app.post("/cart", response_model=CartItemResponse)
def add_to_cart(cart_item: CartItemCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли товар
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Добавляем товар в корзину
    db_cart_item = CartItem(product_id=cart_item.product_id, quantity=cart_item.quantity)
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return CartItemResponse(
        id=db_cart_item.id,
        product_id=db_cart_item.product_id,
        product_name=product.name,
        product_price=product.price,
        quantity=db_cart_item.quantity,
    )


# Удаление товара из корзины
@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Товар в корзине не найден")
    db.delete(cart_item)
    db.commit()
    return {"message": f"Товар с id {item_id} удален из корзины"}


# Добавление товара в магазин
@app.post("/products/", response_model=ProductCreate)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, price=product.price, quantity=product.quantity)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Получение списка товаров
@app.get("/products/")
def read_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

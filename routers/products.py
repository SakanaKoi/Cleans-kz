from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Product, User
from schemas import ProductCreate, ProductUpdate, ProductResponse
from auth.security import get_current_active_admin, get_current_active_user

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# Получение списка доступных товаров
@router.get("/listProducts", response_model=List[ProductResponse])
def list_products(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
):
    products = db.query(Product).filter(Product.available == 1).offset(skip).limit(limit).all()
    return products


# Добавление нового товара (только для администратора)
@router.post("/addProduct", response_model=ProductResponse)
def add_product(
        product: ProductCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Получение информации о товаре по ID
@router.get("/getProduct/{product_id}", response_model=ProductResponse)
def get_product(
        product_id: int,
        db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id, Product.available == 1).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


# Обновление товара (только для администратора)
@router.put("/updateProduct/{product_id}", response_model=ProductResponse)
def update_product(
        product_id: int,
        product_update: ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


# Удаление товара (только для администратора)
@router.delete("/deleteProduct/{product_id}")
def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    db.delete(product)
    db.commit()
    return {"message": f"Товар с id {product_id} удален"}

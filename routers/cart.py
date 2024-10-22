from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import CartItem, User, Product
from schemas import CartItemCreate, CartItemResponse
from auth.security import get_current_active_user

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


# Просмотр корзины
@router.get("/displayCart", response_model=List[CartItemResponse])
def display_cart(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
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
@router.post("/addInCart", response_model=CartItemResponse)
def add_in_cart(
        cart_item: CartItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product or product.available == 0:
        raise HTTPException(status_code=404, detail="Товар не найден или недоступен")

    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == cart_item.product_id
    ).first()

    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        item = existing_item
    else:
        new_cart_item = CartItem(
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        item = new_cart_item

    return CartItemResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=product.name,
        product_price=product.price,
        quantity=item.quantity,
    )


# Удаление товара из корзины
@router.delete("/deleteFromCart/{item_id}")
def delete_from_cart(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Товар в корзине не найден")
    db.delete(cart_item)
    db.commit()
    return {"message": f"Товар с id {item_id} удален из корзины"}


# Очистка корзины
@router.delete("/clearCart")
def clear_cart(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    for item in cart_items:
        db.delete(item)
    db.commit()
    return {"message": "Корзина очищена"}

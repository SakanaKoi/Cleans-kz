from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Order, OrderItem, Product, User, OrderStatus
from schemas import (
    OrderCreate,
    OrderResponse,
    OrderItemResponse,
    OrderStatusUpdate,
)
from auth.security import get_current_active_user, get_current_active_admin

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "/createOrder",
    response_model=OrderResponse,
    summary="Создать заказ",
    description="Создает новый заказ на основе текущей корзины пользователя. После создания заказа корзина очищается.",
    responses={
        200: {"description": "Заказ успешно создан"},
        400: {"description": "Корзина пуста"},
        401: {"description": "Неавторизованный доступ"},
    }
)
def create_order(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    cart_items = db.query(OrderItem).filter(OrderItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    new_order = Order(
        user_id=current_user.id,
        order_date=datetime.utcnow(),
        status=OrderStatus.pending,
        total_price=total_price,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Переносим элементы корзины в позиции заказа
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price,
        )
        db.add(order_item)
        db.delete(item)  # Удаляем из корзины
    db.commit()

    # Формируем ответ
    order_items = db.query(OrderItem).filter(OrderItem.order_id == new_order.id).all()
    return OrderResponse(
        id=new_order.id,
        order_date=new_order.order_date,
        status=new_order.status,
        total_price=new_order.total_price,
        items=[
            OrderItemResponse(
                product_id=order_item.product_id,
                product_name=order_item.product.name,
                quantity=order_item.quantity,
                price=order_item.price,
            )
            for order_item in order_items
        ],
    )


@router.get(
    "/myOrders",
    response_model=List[OrderResponse],
    summary="Мои заказы",
    description="Возвращает список всех заказов текущего пользователя.",
    responses={
        200: {"description": "Список заказов пользователя"},
        401: {"description": "Неавторизованный доступ"},
    }
)
def get_my_orders(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return [
        OrderResponse(
            id=order.id,
            order_date=order.order_date,
            status=order.status,
            total_price=order.total_price,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in order.items
            ],
        )
        for order in orders
    ]


@router.get(
    "/myOrders/{order_id}",
    response_model=OrderResponse,
    summary="Детали заказа",
    description="Возвращает детали конкретного заказа текущего пользователя.",
    responses={
        200: {"description": "Детали заказа"},
        401: {"description": "Неавторизованный доступ"},
        404: {"description": "Заказ не найден"},
    }
)
def get_order_details(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return OrderResponse(
        id=order.id,
        order_date=order.order_date,
        status=order.status,
        total_price=order.total_price,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.items
        ],
    )


@router.delete(
    "/cancelOrder/{order_id}",
    summary="Отмена заказа",
    description="Позволяет пользователю отменить свой заказ, если он еще не обработан.",
    responses={
        200: {"description": "Заказ отменен"},
        400: {"description": "Заказ не может быть отменен"},
        401: {"description": "Неавторизованный доступ"},
        404: {"description": "Заказ не найден"},
    }
)
def cancel_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Заказ не может быть отменен")
    order.status = OrderStatus.cancelled
    db.commit()
    return {"message": f"Заказ с id {order_id} отменен"}


@router.get(
    "/listOrders",
    response_model=List[OrderResponse],
    summary="Список всех заказов",
    description="Возвращает список всех заказов (только для администратора).",
    responses={
        200: {"description": "Список всех заказов"},
        401: {"description": "Неавторизованный доступ"},
        403: {"description": "Недостаточно прав"},
    }
)
def list_all_orders(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    orders = db.query(Order).all()
    return [
        OrderResponse(
            id=order.id,
            order_date=order.order_date,
            status=order.status,
            total_price=order.total_price,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in order.items
            ],
        )
        for order in orders
    ]


@router.put(
    "/updateOrderStatus/{order_id}",
    summary="Обновить статус заказа",
    description="Позволяет администратору обновить статус заказа.",
    responses={
        200: {"description": "Статус заказа обновлен"},
        401: {"description": "Неавторизованный доступ"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Заказ не найден"},
    }
)
def update_order_status(
        order_id: int,
        status_update: OrderStatusUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    order.status = status_update.status
    db.commit()
    return {"message": f"Статус заказа с id {order_id} обновлен на {order.status.value}"}


@router.get(
    "/getOrder/{order_id}",
    response_model=OrderResponse,
    summary="Получить детали заказа",
    description="Возвращает детали указанного заказа (только для администратора).",
    responses={
        200: {"description": "Детали заказа"},
        401: {"description": "Неавторизованный доступ"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Заказ не найден"},
    }
)
def get_order_admin(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return OrderResponse(
        id=order.id,
        order_date=order.order_date,
        status=order.status,
        total_price=order.total_price,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.items
        ],
    )

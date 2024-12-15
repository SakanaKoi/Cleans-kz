import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session

# Добавляем путь к проекту, чтобы можно было импортировать modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database import SessionLocal, engine
from models import User, UserRole, Product, CartItem, Order, OrderItem, OrderStatus
from auth.security import get_password_hash


def create_test_users(db: Session):
    # Проверяем, нет ли уже пользователей
    if db.query(User).count() > 0:
        print("Пользователи уже существуют в БД, пропускаем создание")
        return

    print("Создаем тестовых пользователей...это rofls")
    users_data = [
        {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
            "role": UserRole.client
        },
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "adminpassword",
            "role": UserRole.admin
        }
    ]

    for udata in users_data:
        hashed_password = get_password_hash(udata["password"])
        new_user = User(
            username=udata["username"],
            email=udata["email"],
            hashed_password=hashed_password,
            role=udata["role"]
        )
        db.add(new_user)
    db.commit()
    print("Пользователи созданы успешно.")


def create_test_products(db: Session):
    # Проверяем, нет ли уже товаров
    if db.query(Product).count() > 0:
        print("Товары уже существуют, пропускаем создание.")
        return

    print("Создаем тестовые товары... это не rofls")
    products_data = [
        {
            "name": "Чистка кожаной обуви",
            "description": "Профессиональная чистка кожаной обуви",
            "price": 49.99,
            "category": "Чистка",
            "image_url": "",
            "available": 1
        },
        {
            "name": "Ремонт подошвы",
            "description": "Качественный ремонт подошвы",
            "price": 29.99,
            "category": "Ремонт",
            "image_url": "",
            "available": 1
        },
        {
            "name": "Покраска кожаной обуви",
            "description": "Профессиональная покраска",
            "price": 59.99,
            "category": "Покраска",
            "image_url": "",
            "available": 1
        }
    ]

    for pdata in products_data:
        product = Product(**pdata)
        db.add(product)
    db.commit()
    print("Тестовые товары успешно созданы")


def add_items_to_cart(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"Пользователь {username} не найден, пропускаем добавление товаров в корзину")
        return

    product = db.query(Product).first()
    if not product:
        print("Нет товаров для добавления в корзину")
        return

    print(f"Добавляем товар {product.name} в корзину пользователя {username}")
    cart_item = CartItem(
        user_id=user.id,
        product_id=product.id,
        quantity=2
    )
    db.add(cart_item)
    db.commit()
    print("Товары добавлены в корзину")


def create_test_orders(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"Пользователь {username} не найден, пропускаем создание заказов")
        return

    product = db.query(Product).first()
    if not product:
        print("Нет товаров для создания заказов")
        return

    print(f"Создаем тестовый заказ для пользователя {username}...")
    order = Order(
        user_id=user.id,
        order_date=datetime.utcnow(),
        status=OrderStatus.pending,
        total_price=product.price * 2
    )
    db.add(order)
    db.commit()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        price=product.price
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)

    print(f"Заказ #{order.id} успешно создан для пользователя {username}")


def main():
    db = SessionLocal()
    try:
        create_test_users(db)
        create_test_products(db)
        add_items_to_cart(db, "test_user")
        create_test_orders(db, "test_user")
    finally:
        db.close()


if __name__ == "__main__":
    main()

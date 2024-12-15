from database import SessionLocal
from models import Product


def add_services(db):
    services_data = [
        {
            "name": "Химчистка замшевой обуви",
            "description": "Профессиональная чистка замши, удаление пятен и восстановление текстуры",
            "price": 79.99,
            "category": "Чистка",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Реставрация каблуков",
            "description": "Замена набойки, восстановление каблуков любой сложности",
            "price": 39.99,
            "category": "Ремонт",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Полировка кожаной обуви",
            "description": "Придание блеска и защита от влаги",
            "price": 19.99,
            "category": "Полировка",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Установка защитной подошвы",
            "description": "Продление срока службы обуви с помощью дополнительной подошвы",
            "price": 24.99,
            "category": "Ремонт",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Замена молнии на сапогах",
            "description": "Качественная замена застёжки-молнии, подбор фурнитуры",
            "price": 44.99,
            "category": "Ремонт",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Покраска подошвы",
            "description": "Изменение цвета и реставрация подошвы обуви",
            "price": 29.99,
            "category": "Покраска",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Восстановление цвета нубука",
            "description": "Профессиональная покраска и восстановление насыщенности цвета нубука",
            "price": 59.99,
            "category": "Покраска",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Чистка подошвы кроссовок",
            "description": "Удаление грязи и пятен, возвращение белизны подошве",
            "price": 14.99,
            "category": "Чистка",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Растяжка кожаной обуви",
            "description": "Акуратное растягивание обуви для более комфортной посадки",
            "price": 34.99,
            "category": "Доработка",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        },
        {
            "name": "Антибактериальная обработка",
            "description": "Удаление запахов, бактерий и грибков с внутренней части обуви",
            "price": 9.99,
            "category": "Обработка",
            "image_url": "http://ilyuha_privet/",
            "available": 1
        }
    ]

    # Проверяем, есть ли уже такие услуги в БД
    existing_products = db.query(Product).count()
    if existing_products > 0:
        print(f"В БД уже есть {existing_products} товаров. Новые товары будут добавлены дополнительно.")
    else:
        print("База данных пуста, добавляем новые услуги.")

    for service in services_data:
        new_product = Product(**service)
        db.add(new_product)
    db.commit()

    print(f"Добавлено {len(services_data)} услуг(и).")


def main():
    db = SessionLocal()
    try:
        add_services(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()

from fastapi import FastAPI

from routers import auth, products, cart, users

app = FastAPI(
    title="Сервис чистки обуви",
    description="API для управления сервисом чистки обуви",
    version="1.0.0",
)

# Подключение маршрутов
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(users.router)


# Главная страница
@app.get(
    "/",
    tags=["Main"],
    summary="Главная страница",
    description="Добро пожаловать в сервис чистки обуви!"
)
async def main_page():
    return {"message": "Добро пожаловать в сервис чистки обуви!"}

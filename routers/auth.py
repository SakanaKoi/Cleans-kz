from datetime import timedelta
from fastapi import Depends, HTTPException, status, APIRouter, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import Token, UserCreate, UserResponse
from auth.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
from config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя с ролью клиента.",
    responses={
        400: {"description": "Пользователь с таким именем или email уже существует"},
        200: {"description": "Пользователь успешно зарегистрирован"},
    }
)
def register(
        user: UserCreate = Body(
            ...,
            example={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "strongpassword123"
            }
        ),
        db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем или email уже существует")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Аутентификация пользователя",
    description="Выполняет вход пользователя и возвращает JWT токен для дальнейших запросов.",
    responses={
        200: {"description": "Успешная аутентификация"},
        400: {"description": "Неверное имя пользователя или пароль"},
    }
)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/forgot-password",
    summary="Восстановление пароля",
    description="Отправляет инструкцию по восстановлению пароля на указанный email.",
    responses={
        200: {"description": "Инструкция отправлена на email"},
        404: {"description": "Пользователь с таким email не найден"},
    }
)
def forgot_password(
        email: str = Body(..., example="john@example.com", description="Email пользователя"),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")
    # Логика отправки email (не реализована)
    return {"message": "Инструкция по восстановлению пароля отправлена на ваш email"}

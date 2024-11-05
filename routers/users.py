from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas import UserResponse
from auth.security import get_current_active_admin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Получение списка пользователей (только для администратора)
@router.get(
    "/listUsers",
    response_model=List[UserResponse],
    summary="Список пользователей",
    description="Получение списка всех пользователей (только для администратора).",
    responses={
        200: {"description": "Список пользователей"},
        401: {"description": "Неавторизованный доступ"},
        403: {"description": "Недостаточно прав"},
    }
)
def list_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
        skip: int = 0,
        limit: int = 100,
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# Получение информации о пользователе по ID (только для администратора)
@router.get(
    "/getUser/{user_id}",
    response_model=UserResponse,
    summary="Получить информацию о пользователе",
    description="Возвращает информацию о пользователе по его ID (только для администратора).",
    responses={
        200: {"description": "Информация о пользователе"},
        404: {"description": "Пользователь не найден"},
        401: {"description": "Неавторизованный доступ"},
        403: {"description": "Недостаточно прав"},
    }
)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# Деактивация пользователя (только для администратора)
@router.put(
    "/deactivateUser/{user_id}",
    summary="Деактивировать пользователя",
    description="Деактивирует учетную запись пользователя (только для администратора).",
    responses={
        200: {"description": "Пользователь успешно деактивирован"},
        404: {"description": "Пользователь не найден"},
        401: {"description": "Неавторизованный доступ"},
        403: {"description": "Недостаточно прав"},
    }
)
def deactivate_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_active = 0
    db.commit()
    return {"message": f"Пользователь с id {user_id} деактивирован"}

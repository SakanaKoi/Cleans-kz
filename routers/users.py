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
@router.get("/listUsers", response_model=List[UserResponse])
def list_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_admin),
        skip: int = 0,
        limit: int = 100,
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# Получение информации о пользователе по ID (только для администратора)
@router.get("/getUser/{user_id}", response_model=UserResponse)
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
@router.put("/deactivateUser/{user_id}")
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

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Подключение к базе данных PostgreSQL
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Получение сессии для работы с базой данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

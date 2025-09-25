from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

def get_db_session() -> Session:
    return Depends(get_db)
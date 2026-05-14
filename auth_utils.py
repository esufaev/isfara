from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import Customer

SECRET_KEY = "super_secret_key_isfara_change_me_in_production"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Внимание: Неверный формат хэша в БД: {e}")
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
            
        user_id = int(user_id_str)
        
    except JWTError as e:
        print(f"Ошибка декодирования JWT: {e}")
        raise HTTPException(status_code=401, detail="Токен истек или недействителен")
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный формат ID в токене")
    
    result = await db.execute(select(Customer).where(Customer.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    user.role = role
    return user

def require_roles(allowed_roles: list):
    async def role_checker(current_user: Customer = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Недостаточно прав для доступа (Требуется роль администратора)")
        return current_user
    return role_checker

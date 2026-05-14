from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import Customer
from auth_utils import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
async def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    middle_name: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Customer).where(Customer.email == email))
    if result.scalar_one_or_none():
        request.session["flash_msg"] = "Ошибка: Данный Email уже зарегистрирован!"
        return RedirectResponse(url="/register", status_code=302)

    new_user = Customer(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        phone=phone,
        email=email,
        password_hash=get_password_hash(password)
    )
    db.add(new_user)
    await db.commit()
    
    request.session["flash_msg"] = f"Успешная регистрация! Добро пожаловать, {first_name}. Теперь вы можете войти."
    return RedirectResponse(url="/login", status_code=302)


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Customer).where(Customer.email == email))
    db_user = result.scalar_one_or_none()
    
    if not db_user or not verify_password(password, db_user.password_hash):
        request.session["flash_msg"] = "Неверный email или пароль!"
        return RedirectResponse(url="/login", status_code=302)
    
    role = "admin" if db_user.email == "admin@isfara.ru" else "guest"
    token = create_access_token({"sub": str(db_user.id), "role": role})
    
    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(
        key="access_token", 
        value=token, 
        httponly=True, 
        max_age=86400,
        samesite="lax"
    )
    
    return response


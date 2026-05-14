from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    password: str
    middle_name: Optional[str] = None
    kladr_code: Optional[str] = None # <-- ИЗМЕНИЛИ НА str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class MenuItem(BaseModel):
    item_id: int
    item_name: str
    description: Optional[str]
    category_name: Optional[str]
    price: float

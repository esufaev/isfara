# --- START OF FILE models.py ---
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(72), nullable=False)
    registration_date = Column(DateTime, server_default=func.now())
    kladr_code = Column(String(20))

class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    kladr_code = Column(String(20))
    phone = Column(String(20))

class MenuCategory(Base):
    __tablename__ = "menu_categories"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("menu_categories.id"))
    name = Column(String(100), nullable=False)

class MenuItemModel(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("menu_categories.id"))
    name = Column(String(50), nullable=False)
    base_price = Column(Float, nullable=False)
    description = Column(String)
    image_url = Column(String) # <--- ДОБАВЛЕНО ДЛЯ КАРТИНОК

class BranchMenu(Base):
    __tablename__ = "branch_menu"
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id")) 
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    local_price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
# --- END OF FILE models.py ---

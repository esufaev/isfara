# --- START OF FILE routers/menu.py ---
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from datetime import datetime

from database import get_db
from models import MenuItemModel, MenuCategory, BranchMenu

router = APIRouter(prefix="/api/menu", tags=["Menu"])

MENU_CACHE = {"data": None, "last_updated": None}
CACHE_TTL = 60 

@router.get("/{branch_id}")
async def get_menu(
    branch_id: int, 
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now()
    if MENU_CACHE["data"] and MENU_CACHE["last_updated"]:
        if (now - MENU_CACHE["last_updated"]).total_seconds() < CACHE_TTL:
            items = MENU_CACHE["data"]
            if category:
                items = [i for i in items if i["category_name"] == category]
            return items

    query = (
        select(
            MenuItemModel.id.label("item_id"),
            MenuItemModel.name.label("item_name"),
            MenuItemModel.description,
            MenuItemModel.image_url, # <--- ДОБАВЛЕНО
            MenuCategory.name.label("category_name"),
            BranchMenu.local_price.label("price")
        )
        .select_from(BranchMenu)
        .join(MenuItemModel, BranchMenu.menu_item_id == MenuItemModel.id)
        .outerjoin(MenuCategory, MenuItemModel.category_id == MenuCategory.id)
        .where(BranchMenu.branch_id == branch_id)
        .where(BranchMenu.is_available == True)
    )
        
    result = await db.execute(query)
    records = result.all()
    
    items = [{
        "item_id": r.item_id, 
        "item_name": r.item_name, 
        "description": r.description, 
        "image_url": r.image_url, # <--- ДОБАВЛЕНО
        "category_name": r.category_name, 
        "price": r.price
    } for r in records]

    if not category:
        MENU_CACHE["data"] = items
        MENU_CACHE["last_updated"] = now

    return items
# --- END OF FILE routers/menu.py ---

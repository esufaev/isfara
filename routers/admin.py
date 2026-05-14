from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import Customer, MenuItemModel, BranchMenu, Branch
from auth_utils import get_current_user, require_roles
from routers.menu import MENU_CACHE

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    current_user: Customer = Depends(require_roles(["admin"]))
):
    users_result = await db.execute(select(Customer))
    db_users = users_result.scalars().all()
    
    users = []
    for u in db_users:
        users.append({
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "role": "admin" if u.email == "admin@isfara.ru" else "guest"
        })
    
    branches_result = await db.execute(select(Branch))
    branches = branches_result.scalars().all()
    
    flash_msg = request.session.pop("flash_msg", None)
    
    return templates.TemplateResponse(request=request, name="admin.html", context={
        "users": users, 
        "branches": branches, 
        "current_user": current_user,
        "flash_msg": flash_msg
    })

@router.post("/menu/add")
async def add_menu_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    branch_id: int = Form(...),
    image_url: str = Form(""), 
    db: AsyncSession = Depends(get_db),
    current_user: Customer = Depends(require_roles(["admin"]))
):
    new_item = MenuItemModel(
        name=name, 
        description=description, 
        base_price=price,
        image_url=image_url if image_url else None 
    )
    db.add(new_item)
    await db.flush() 
    
    new_branch_menu = BranchMenu(
        branch_id=branch_id,
        menu_item_id=new_item.id,
        local_price=price,
        is_available=True
    )
    db.add(new_branch_menu)
    await db.commit()
    
    MENU_CACHE["data"] = None
    MENU_CACHE["last_updated"] = None
    
    request.session["flash_msg"] = f"Блюдо «{name}» успешно добавлено в меню филиала!"
    return RedirectResponse(url="/admin/dashboard", status_code=303)


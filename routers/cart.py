from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter(prefix="/api/cart", tags=["Cart"])

@router.post("/add")
async def add_to_cart(
    request: Request,
    item_id: str = Form(...),
    name: str = Form(...),
    price: float = Form(...),
    image_url: str = Form("")
):
    
    cart = request.session.get("cart", {})
    
    if item_id in cart:
        cart[item_id]["quantity"] += 1
    else:
        cart[item_id] = {
            "id": item_id,
            "name": name,
            "price": price,
            "image_url": image_url,
            "quantity": 1
        }
        
    request.session["cart"] = cart
    
    total_items = sum(item["quantity"] for item in cart.values())
    return JSONResponse({"status": "success", "total_items": total_items})

@router.get("/count")
async def get_cart_count(request: Request):
    """Эндпоинт для получения количества товаров (используется в JS для бейджика)"""
    cart = request.session.get("cart", {})
    count = sum(item["quantity"] for item in cart.values())
    return JSONResponse({"count": count})

@router.post("/update")
async def update_cart(request: Request, item_id: str = Form(...), action: str = Form(...)):
    """Увеличение или уменьшение количества товара в корзине"""
    cart = request.session.get("cart", {})
    
    if item_id in cart:
        if action == "increase":
            cart[item_id]["quantity"] += 1
        elif action == "decrease":
            cart[item_id]["quantity"] -= 1
            if cart[item_id]["quantity"] <= 0:
                del cart[item_id]
                
    request.session["cart"] = cart
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/remove")
async def remove_from_cart(request: Request, item_id: str = Form(...)):
    """Полное удаление товара из корзины"""
    cart = request.session.get("cart", {})
    if item_id in cart:
        del cart[item_id]
        request.session["cart"] = cart
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/clear")
async def clear_cart(request: Request):
    """Очистить корзину полностью"""
    request.session["cart"] = {}
    return RedirectResponse(url="/cart", status_code=303)


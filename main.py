from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from database import get_db
from routers import auth, menu, admin, cart
from auth_utils import get_current_user, SECRET_KEY, ALGORITHM

app = FastAPI(title="Кафе Исфара API")

app.add_middleware(SessionMiddleware, secret_key="session_super_secret")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(admin.router)
app.include_router(cart.router)

@app.middleware("http")
async def add_user_role_to_request(request: Request, call_next):
    request.state.user_role = None
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_role = payload.get("role")
        except:
            pass
    
    response = await call_next(request)
    return response

@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/login")
async def serve_login(request: Request):
    flash_msg = request.session.pop("flash_msg", None)
    return templates.TemplateResponse(request=request, name="login.html", context={"flash_msg": flash_msg})

@app.get("/register")
async def serve_register(request: Request):
    flash_msg = request.session.pop("flash_msg", None)
    return templates.TemplateResponse(request=request, name="register.html", context={"flash_msg": flash_msg})

@app.get("/profile")
async def serve_profile(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user = await get_current_user(request, db)
    except Exception as e:
        return RedirectResponse(url="/login", status_code=302)

    flash_msg = request.session.pop("flash_msg", None)

    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role
    }

    return templates.TemplateResponse(request=request, name="profile.html", context={
        "user": user_data,
        "flash_msg": flash_msg
    })

@app.get("/cart")
async def serve_cart(request: Request):
    cart_data = request.session.get("cart", {})
    
    
    total_price = sum(item["price"] * item["quantity"] for item in cart_data.values())
    
    return templates.TemplateResponse(request=request, name="cart.html", context={
        "cart": cart_data,
        "total_price": total_price
    })

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    request.session.clear()
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


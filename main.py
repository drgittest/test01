from starlette.applications import Starlette
from starlette.responses import RedirectResponse, HTMLResponse, JSONResponse
from starlette.routing import Route
from middleware import JWTAuthMiddleware 
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware

from models import Base, User, settings, Order
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ユーザー登録
async def register(request: Request):
    print("register handler called, method:", request.method)
    if request.method == "GET":
        return templates.TemplateResponse("register.html", {"request": request, "error": None})
    form = await request.form()
    print("register form data:", form)
    login_id = form.get("login_id")
    password = form.get("password")
    with SessionLocal() as db:
        if db.query(User).filter_by(login_id=login_id).first():
            return templates.TemplateResponse("register.html", {"request": request, "error": "既に存在します"})
        user = User(login_id=login_id, password=password)
        db.add(user)
        db.commit()
    return RedirectResponse("/login", status_code=302)

# ログイン
async def login(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("login.html", {"request": request, "error": None})
    form = await request.form()
    login_id = form.get("login_id")
    password = form.get("password")
    with SessionLocal() as db:
        user = db.query(User).filter_by(login_id=login_id, password=password).first()
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "IDまたはパスワードが違います"})
    payload = {"user_id": user.login_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    response = RedirectResponse("/", status_code=302)
    request.session["access_token"] = token
    return response

# ログアウト
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

# 認証付きトップページ
async def index(request: Request):
    user = getattr(request.state, "user", None)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# --- Order Handlers ---

async def list_orders(request: Request):
    with SessionLocal() as db:
        orders = db.query(Order).all()
    return templates.TemplateResponse("orders.html", {"request": request, "orders": orders})

async def create_order(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("order_create.html", {"request": request, "error": None})
    form = await request.form()
    order_number = form.get("order_number")
    customer_name = form.get("customer_name")
    item = form.get("item")
    quantity = form.get("quantity")
    price = form.get("price")
    status = form.get("status", "pending")
    now = datetime.now().isoformat()
    with SessionLocal() as db:
        order = Order(
            order_number=order_number,
            customer_name=customer_name,
            item=item,
            quantity=int(quantity),
            price=int(price),
            status=status,
            created_at=now,
            updated_at=now
        )
        db.add(order)
        db.commit()
    return RedirectResponse("/orders", status_code=302)

async def get_order_api(request: Request):
    """
    JSON API endpoint for getting order details by ID
    
    Args:
        request: Starlette Request object containing order_id in path params
        
    Returns:
        JSONResponse: Order data as JSON or error response
        
    Raises:
        404: When order with specified ID is not found
        400: When order_id parameter is invalid
    """
    try:
        # Extract and validate order_id parameter
        order_id = request.path_params["order_id"]
        if not order_id or not str(order_id).isdigit():
            return JSONResponse(
                {"error": "Invalid order ID format", "details": "Order ID must be a positive integer"}, 
                status_code=400
            )
        
        order_id = int(order_id)
        
        # Query database for order
        with SessionLocal() as db:
            order = db.query(Order).filter_by(id=order_id).first()
            
        if not order:
            return JSONResponse(
                {"error": "Order not found", "order_id": order_id}, 
                status_code=404
            )
        
        # Return order data as JSON
        return JSONResponse({
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "item": order.item,
            "quantity": order.quantity,
            "price": order.price,
            "status": order.status,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        })
        
    except Exception as e:
        # Log unexpected errors
        print(f"Error in get_order_api: {str(e)}")
        return JSONResponse(
            {"error": "Internal server error", "details": "An unexpected error occurred"}, 
            status_code=500
        )

async def edit_order(request: Request):
    order_id = request.path_params["order_id"]
    with SessionLocal() as db:
        order = db.query(Order).filter_by(id=order_id).first()
        if not order:
            return HTMLResponse("Order not found", status_code=404)
        if request.method == "GET":
            return templates.TemplateResponse("order_edit.html", {"request": request, "order": order, "error": None})
        form = await request.form()
        order.order_number = form.get("order_number")
        order.customer_name = form.get("customer_name")
        order.item = form.get("item")
        order.quantity = int(form.get("quantity"))
        order.price = int(form.get("price"))
        order.status = form.get("status", order.status)
        order.updated_at = datetime.now().isoformat()
        db.commit()
    return RedirectResponse("/orders", status_code=302)

routes = [
    Route("/", index),
    Route("/register", register, methods=["GET", "POST"]),
    Route("/login", login, methods=["GET", "POST"]),
    Route("/logout", logout),
    # Order routes
    Route("/orders", list_orders),
    Route("/orders/", list_orders),
    Route("/orders/create", create_order, methods=["GET", "POST"]),
    Route("/api/orders/{order_id}", get_order_api),
    Route("/orders/{order_id}/edit", edit_order, methods=["GET", "POST"]),
]

app = Starlette(
    routes=routes,
    middleware=[
        Middleware(SessionMiddleware, secret_key="session_secret_key"),
        Middleware(JWTAuthMiddleware)
    ]
)

# Serve static assets (built Tailwind CSS, images, etc.)
from starlette.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

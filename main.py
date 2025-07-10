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

from models import Base, User, settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

routes = [
    Route("/", index),
    Route("/register", register, methods=["GET", "POST"]),
    Route("/login", login, methods=["GET", "POST"]),
    Route("/logout", logout),
]

app = Starlette(
    routes=routes,
    middleware=[
        Middleware(SessionMiddleware, secret_key="session_secret_key"),
        Middleware(JWTAuthMiddleware)
    ]
)

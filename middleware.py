from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from jose import jwt

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Allow all requests to /login, /register, /orders, and /orders/create (with or without trailing slash)
        if request.url.path.rstrip('/') in ["/login", "/register", "/orders", "/orders/create"]:
            return await call_next(request)
        token = request.session.get("access_token")
        if not token:
            return RedirectResponse("/login")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = payload
        except jwt.InvalidTokenError:
            return RedirectResponse("/login")
        return await call_next(request)

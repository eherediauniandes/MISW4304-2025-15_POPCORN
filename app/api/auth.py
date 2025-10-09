import hmac
from flask import request, current_app
from functools import wraps

def static_bearer_required(fn):
    """Decorator to protect routes with a static bearer token."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return {"message": "Unauthorized"}, 401
        token = auth.split("Bearer ", 1)[1].strip()

        expected = current_app.config["STATIC_JWT_TOKEN"]
        if not token or not hmac.compare_digest(token, expected):
            return {"message": "Forbidden"}, 403
        return fn(*args, **kwargs)
    return wrapper

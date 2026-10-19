"""JWT 鉴权工具与装饰器"""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .response import Err, fail


def create_token(user_id, role):
    """签发 JWT token"""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=current_app.config["TOKEN_EXPIRE_HOURS"]),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _decode_token(token):
    """解析 token，失败返回 None"""
    try:
        return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def _auth_context():
    """从 Authorization: Bearer <token> 解析并注入 g.user_id / g.role，返回错误响应或 None"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(fail(Err.UNAUTHORIZED, "未登录或 token 缺失")), 401
    payload = _decode_token(auth[7:])
    if not payload:
        return jsonify(fail(Err.UNAUTHORIZED, "token 无效或已过期")), 401
    g.user_id = payload["user_id"]
    g.role = payload["role"]
    return None


def login_required(view):
    """要求登录"""
    @wraps(view)
    def wrapper(*args, **kwargs):
        err = _auth_context()
        if err:
            return err
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    """要求管理员权限"""
    @wraps(view)
    def wrapper(*args, **kwargs):
        err = _auth_context()
        if err:
            return err
        if g.role != "admin":
            return jsonify(fail(Err.FORBIDDEN, "无管理员权限")), 403
        return view(*args, **kwargs)
    return wrapper

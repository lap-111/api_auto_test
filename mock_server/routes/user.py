"""用户模块接口：注册、登录、个人信息"""
from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from ..auth import create_token, login_required
from ..models import User, db
from ..response import Err, fail, ok

user_bp = Blueprint("user", __name__, url_prefix="/api/users")


@user_bp.post("/register")
def register():
    """注册：username/password 必填，nickname 可选"""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    nickname = (data.get("nickname") or "").strip()

    if not username or not password:
        return jsonify(fail(Err.PARAM_ERROR, "用户名和密码不能为空")), 400
    if not 3 <= len(username) <= 20:
        return jsonify(fail(Err.PARAM_ERROR, "用户名长度需在 3-20 之间")), 400
    if not 6 <= len(password) <= 20:
        return jsonify(fail(Err.PARAM_ERROR, "密码长度需在 6-20 之间")), 400
    if User.query.filter_by(username=username).first():
        return jsonify(fail(Err.USER_EXISTS, "用户名已存在")), 200

    user = User(username=username, password=generate_password_hash(password),
                nickname=nickname or username)
    db.session.add(user)
    db.session.commit()
    return jsonify(ok(user.to_dict(), "注册成功")), 200


@user_bp.post("/login")
def login():
    """登录：校验通过返回 token"""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify(fail(Err.PARAM_ERROR, "用户名和密码不能为空")), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(fail(Err.USER_NOT_FOUND, "用户不存在")), 200
    if not check_password_hash(user.password, password):
        return jsonify(fail(Err.WRONG_PASSWORD, "密码错误")), 200

    token = create_token(user.id, user.role)
    return jsonify(ok({"token": token, "user": user.to_dict()}, "登录成功")), 200


@user_bp.get("/me")
@login_required
def get_me():
    """获取当前登录用户信息"""
    user = User.query.get(g.user_id)
    return jsonify(ok(user.to_dict())), 200


@user_bp.put("/me")
@login_required
def update_me():
    """修改当前用户资料（昵称）"""
    data = request.get_json(silent=True) or {}
    nickname = (data.get("nickname") or "").strip()
    if not nickname:
        return jsonify(fail(Err.PARAM_ERROR, "昵称不能为空")), 400
    user = User.query.get(g.user_id)
    user.nickname = nickname
    db.session.commit()
    return jsonify(ok(user.to_dict(), "修改成功")), 200

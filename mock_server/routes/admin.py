"""后台管理接口：管理员登录、新增商品、上架/下架"""
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

from ..auth import admin_required, create_token
from ..models import Product, User, db
from ..response import Err, fail, ok

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.post("/login")
def admin_login():
    """管理员登录：仅 role=admin 可登录成功"""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password) or user.role != "admin":
        return jsonify(fail(Err.FORBIDDEN, "管理员账号或密码错误")), 200
    token = create_token(user.id, user.role)
    return jsonify(ok({"token": token, "user": user.to_dict()}, "登录成功")), 200


@admin_bp.post("/products")
@admin_required
def create_product():
    """新增商品"""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    price = data.get("price")
    stock = data.get("stock")
    category = (data.get("category") or "").strip()
    if not name or not isinstance(price, (int, float)) or price <= 0 \
            or not isinstance(stock, int) or stock < 0 or not category:
        return jsonify(fail(Err.PARAM_ERROR, "参数错误：name/price/category 必填，stock 需为非负整数")), 400

    product = Product(name=name, price=price, stock=stock, category=category,
                      description=data.get("description", ""))
    db.session.add(product)
    db.session.commit()
    return jsonify(ok(product.to_dict(), "商品创建成功")), 200


@admin_bp.put("/products/<int:product_id>/status")
@admin_required
def update_product_status(product_id):
    """上架(on)/下架(off)商品"""
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("on", "off"):
        return jsonify(fail(Err.PARAM_ERROR, "status 需为 on 或 off")), 400
    product = Product.query.get(product_id)
    if not product:
        return jsonify(fail(Err.PRODUCT_NOT_FOUND, "商品不存在")), 200
    product.status = status
    db.session.commit()
    return jsonify(ok(product.to_dict(), "操作成功")), 200

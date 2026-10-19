"""购物车模块接口：加购、列表、改数量、删除"""
from flask import Blueprint, g, jsonify, request

from ..auth import login_required
from ..models import CartItem, Product, db
from ..response import Err, fail, ok

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


@cart_bp.post("/items")
@login_required
def add_item():
    """加购：product_id 必填，quantity 默认 1，数量不能超过库存"""
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id or not isinstance(quantity, int) or quantity < 1:
        return jsonify(fail(Err.PARAM_ERROR, "参数错误：product_id 必填，quantity 需为正整数")), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify(fail(Err.PRODUCT_NOT_FOUND, "商品不存在")), 200
    if product.status != "on":
        return jsonify(fail(Err.PRODUCT_OFF_SHELF, "商品已下架")), 200
    if quantity > product.stock:
        return jsonify(fail(Err.STOCK_NOT_ENOUGH, "加购数量超过库存")), 200

    item = CartItem.query.filter_by(user_id=g.user_id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=g.user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    return jsonify(ok({"id": item.id, "product_id": product_id, "quantity": item.quantity}, "加购成功")), 200


@cart_bp.get("")
@login_required
def get_cart():
    """查看购物车（附带商品信息）"""
    items = CartItem.query.filter_by(user_id=g.user_id).all()
    result = []
    for item in items:
        product = Product.query.get(item.product_id)
        result.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "price": product.price if product else None,
            "quantity": item.quantity,
            "total": round(product.price * item.quantity, 2) if product else None,
        })
    return jsonify(ok({"items": result})), 200


@cart_bp.put("/items/<int:item_id>")
@login_required
def update_item(item_id):
    """修改购物车项数量"""
    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify(fail(Err.PARAM_ERROR, "quantity 需为正整数")), 400

    item = CartItem.query.filter_by(id=item_id, user_id=g.user_id).first()
    if not item:
        return jsonify(fail(Err.CART_ITEM_NOT_FOUND, "购物车项不存在")), 200
    item.quantity = quantity
    db.session.commit()
    return jsonify(ok({"id": item.id, "quantity": item.quantity}, "修改成功")), 200


@cart_bp.delete("/items/<int:item_id>")
@login_required
def remove_item(item_id):
    """删除购物车项"""
    item = CartItem.query.filter_by(id=item_id, user_id=g.user_id).first()
    if not item:
        return jsonify(fail(Err.CART_ITEM_NOT_FOUND, "购物车项不存在")), 200
    db.session.delete(item)
    db.session.commit()
    return jsonify(ok(None, "删除成功")), 200

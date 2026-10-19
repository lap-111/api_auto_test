"""订单模块接口：下单、列表、详情、取消、支付、确认收货

订单状态机：pending(待支付) -> paid(已支付) -> completed(已完成)
                        \-> canceled(已取消)
约束：仅 pending 可取消/支付；仅 paid 可确认收货；非法流转返回 5002。
"""
import uuid
from datetime import datetime

from flask import Blueprint, g, jsonify, request

from ..auth import login_required
from ..models import CartItem, Order, OrderItem, Product, User, db
from ..response import Err, fail, ok

order_bp = Blueprint("order", __name__, url_prefix="/api/orders")

STATUS_PENDING = "pending"
STATUS_PAID = "paid"
STATUS_COMPLETED = "completed"
STATUS_CANCELED = "canceled"


def _gen_order_no():
    return datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:6]


def _order_items(order_id):
    return OrderItem.query.filter_by(order_id=order_id).all()


@order_bp.post("")
@login_required
def create_order():
    """从购物车下单：可选 cart_item_ids 指定项，默认全部。下单扣减库存并清空对应购物车项"""
    data = request.get_json(silent=True) or {}
    cart_item_ids = data.get("cart_item_ids")

    query = CartItem.query.filter_by(user_id=g.user_id)
    if cart_item_ids:
        query = query.filter(CartItem.id.in_(cart_item_ids))
    cart_items = query.all()
    if not cart_items:
        return jsonify(fail(Err.CART_EMPTY, "购物车为空或指定的购物车项不存在")), 200

    # 校验商品与库存
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if not product or product.status != "on":
            return jsonify(fail(Err.PRODUCT_NOT_FOUND, f"商品 {item.product_id} 不存在或已下架")), 200
        if product.stock < item.quantity:
            return jsonify(fail(Err.STOCK_NOT_ENOUGH, f"商品 {product.name} 库存不足")), 200

    order = Order(order_no=_gen_order_no(), user_id=g.user_id,
                  status=STATUS_PENDING, total_amount=0)
    db.session.add(order)
    db.session.flush()  # 获取 order.id

    total = 0.0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        product.stock -= item.quantity
        total += product.price * item.quantity
        db.session.add(OrderItem(order_id=order.id, product_id=product.id,
                                 product_name=product.name, price=product.price,
                                 quantity=item.quantity))
        db.session.delete(item)

    order.total_amount = round(total, 2)
    db.session.commit()
    return jsonify(ok(order.to_dict(_order_items(order.id)), "下单成功")), 200


@order_bp.get("")
@login_required
def list_orders():
    """订单列表（仅本人，分页）"""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    query = Order.query.filter_by(user_id=g.user_id)
    total = query.count()
    orders = query.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return jsonify(ok({
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [o.to_dict(_order_items(o.id)) for o in orders],
    })), 200


@order_bp.get("/<int:order_id>")
@login_required
def get_order(order_id):
    """订单详情（仅本人）"""
    order = Order.query.filter_by(id=order_id, user_id=g.user_id).first()
    if not order:
        return jsonify(fail(Err.ORDER_NOT_FOUND, "订单不存在")), 200
    return jsonify(ok(order.to_dict(_order_items(order.id)))), 200


@order_bp.post("/<int:order_id>/cancel")
@login_required
def cancel_order(order_id):
    """取消订单：仅 pending 可取消，返还库存"""
    order = Order.query.filter_by(id=order_id, user_id=g.user_id).first()
    if not order:
        return jsonify(fail(Err.ORDER_NOT_FOUND, "订单不存在")), 200
    if order.status != STATUS_PENDING:
        return jsonify(fail(Err.ORDER_STATE_INVALID, "仅待支付订单可取消")), 200

    items = _order_items(order.id)
    for item in items:  # 返还库存
        product = Product.query.get(item.product_id)
        if product:
            product.stock += item.quantity
    order.status = STATUS_CANCELED
    db.session.commit()
    return jsonify(ok(order.to_dict(items), "订单已取消")), 200


@order_bp.post("/<int:order_id>/pay")
@login_required
def pay_order(order_id):
    """支付订单：仅 pending 可支付，校验余额并扣减"""
    order = Order.query.filter_by(id=order_id, user_id=g.user_id).first()
    if not order:
        return jsonify(fail(Err.ORDER_NOT_FOUND, "订单不存在")), 200
    if order.status == STATUS_PAID:
        return jsonify(fail(Err.ORDER_ALREADY_PAID, "订单已支付，请勿重复支付")), 200
    if order.status != STATUS_PENDING:
        return jsonify(fail(Err.ORDER_STATE_INVALID, "当前订单状态不可支付")), 200

    user = User.query.get(g.user_id)
    if user.balance < order.total_amount:
        return jsonify(fail(Err.BALANCE_NOT_ENOUGH, "余额不足")), 200

    user.balance -= order.total_amount
    order.status = STATUS_PAID
    order.paid_at = datetime.now()
    db.session.commit()
    return jsonify(ok(order.to_dict(_order_items(order.id)), "支付成功")), 200


@order_bp.post("/<int:order_id>/confirm")
@login_required
def confirm_order(order_id):
    """确认收货：仅 paid 可完成"""
    order = Order.query.filter_by(id=order_id, user_id=g.user_id).first()
    if not order:
        return jsonify(fail(Err.ORDER_NOT_FOUND, "订单不存在")), 200
    if order.status != STATUS_PAID:
        return jsonify(fail(Err.ORDER_STATE_INVALID, "仅已支付订单可确认收货")), 200
    order.status = STATUS_COMPLETED
    db.session.commit()
    return jsonify(ok(order.to_dict(_order_items(order.id)), "确认收货成功")), 200

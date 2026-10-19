"""商品模块接口：列表（分页/筛选/搜索）、详情"""
from flask import Blueprint, jsonify, request

from ..models import Product
from ..response import Err, fail, ok

product_bp = Blueprint("product", __name__, url_prefix="/api/products")


@product_bp.get("")
def list_products():
    """商品列表：page/page_size 分页，category 分类筛选，keyword 名称模糊搜索；仅返回上架商品"""
    # 分页边界约束：page>=1，page_size 限制在 1-100
    page = max(1, request.args.get("page", 1, type=int) or 1)
    page_size = max(1, min(request.args.get("page_size", 10, type=int) or 10, 100))
    category = request.args.get("category", "").strip()
    keyword = request.args.get("keyword", "").strip()

    query = Product.query.filter_by(status="on")
    if category:
        query = query.filter_by(category=category)
    if keyword:
        query = query.filter(Product.name.contains(keyword))

    total = query.count()
    products = query.order_by(Product.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return jsonify(ok({
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [p.to_dict() for p in products],
    })), 200


@product_bp.get("/<int:product_id>")
def get_product(product_id):
    """商品详情"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify(fail(Err.PRODUCT_NOT_FOUND, "商品不存在")), 200
    return jsonify(ok(product.to_dict())), 200

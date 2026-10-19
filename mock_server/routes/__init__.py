"""注册所有业务路由"""
from .admin import admin_bp
from .cart import cart_bp
from .order import order_bp
from .product import product_bp
from .user import user_bp

__all__ = ["admin_bp", "cart_bp", "order_bp", "product_bp", "user_bp"]

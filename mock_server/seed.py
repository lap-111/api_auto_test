"""初始化种子数据：管理员账号与示例商品"""
from werkzeug.security import generate_password_hash

from .models import Product, User, db

PRODUCTS = [
    {"name": "iPhone 15 Pro", "price": 7999.0, "stock": 50, "category": "手机", "description": "256GB 原色钛金属"},
    {"name": "小米 14", "price": 3999.0, "stock": 80, "category": "手机", "description": "8GB+256GB 黑色"},
    {"name": "MacBook Air M2", "price": 9499.0, "stock": 30, "category": "笔记本", "description": "8GB+256GB 午夜色"},
    {"name": "ThinkPad X1", "price": 10999.0, "stock": 20, "category": "笔记本", "description": "i7/16GB/512GB"},
    {"name": "罗技鼠标 M590", "price": 249.0, "stock": 200, "category": "配件", "description": "静音无线"},
    {"name": "机械键盘 K87", "price": 399.0, "stock": 150, "category": "配件", "description": "茶轴 RGB"},
    {"name": "USB-C 扩展坞", "price": 199.0, "stock": 120, "category": "配件", "description": "七合一"},
    {"name": "无线充电器", "price": 129.0, "stock": 300, "category": "配件", "description": "15W"},
    {"name": "降噪耳机 WH-1000XM5", "price": 2399.0, "stock": 40, "category": "音频", "description": "头戴式"},
    {"name": "蓝牙音箱 JBL Go3", "price": 269.0, "stock": 100, "category": "音频", "description": "便携防水"},
]


def seed_data():
    """幂等初始化：仅在数据为空时写入"""
    if User.query.count() == 0:
        db.session.add_all([
            User(username="admin", password=generate_password_hash("admin123"),
                 nickname="管理员", role="admin", balance=0),
            User(username="user01", password=generate_password_hash("123456"),
                 nickname="测试用户", balance=10000),
        ])
    if Product.query.count() == 0:
        db.session.add_all([Product(**p) for p in PRODUCTS])
    db.session.commit()

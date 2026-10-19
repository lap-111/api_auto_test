"""Mock 商城服务配置"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # JWT 签名密钥（mock 环境固定即可）
    SECRET_KEY = "mall-mock-secret-2026"
    # 登录态有效期（小时）
    TOKEN_EXPIRE_HOURS = 2
    # SQLite 数据库文件路径
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "mall.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 新用户注册初始余额（测试友好）
    DEFAULT_BALANCE = 10000

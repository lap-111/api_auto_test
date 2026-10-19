"""测试数据工厂：场景用例造数工具

- create_user(): 注册并登录新用户，返回用户信息与 token
- admin_login(): 管理员登录，返回 token
- create_product(): 创建新商品（需处于管理员登录态）

场景用例通过 TokenSwitch 临时切换 client 的登录态，实现多用户数据隔离。
"""
import uuid

from core.logger import get_logger


def random_username(prefix="auto"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TokenSwitch:
    """临时切换 client token 的上下文管理器，退出时恢复原 token"""

    def __init__(self, client, token):
        self.client = client
        self.token = token
        self._saved = client.token

    def __enter__(self):
        self.client.set_token(self.token)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.set_token(self._saved)


class Factory:
    """场景用例数据工厂：持有全部接口对象与造数方法"""

    def __init__(self, user_api, admin_api, product_api, cart_api, order_api):
        self.user_api = user_api
        self.admin_api = admin_api
        self.product_api = product_api
        self.cart_api = cart_api
        self.order_api = order_api
        self.logger = get_logger("factory")

    def create_user(self):
        """注册并登录一个新用户，返回 {username, password, token, user}"""
        username = random_username()
        password = "abc123"
        resp = self.user_api.register(username, password)
        assert resp.code == 0, f"创建用户失败: {resp.msg}"
        resp = self.user_api.login(username, password)
        return {"username": username, "password": password,
                "token": resp.data["token"], "user": resp.data["user"]}

    def admin_login(self):
        """管理员登录，返回 token"""
        resp = self.admin_api.login("admin", "admin123")
        assert resp.code == 0, f"管理员登录失败: {resp.msg}"
        return resp.data["token"]

    def create_product(self, price=99.9, stock=10, category="测试", name=None):
        """创建新商品（需处于管理员登录态），返回商品 id"""
        resp = self.admin_api.create_product(name=name or random_username("prod"),
                                             price=price, stock=stock, category=category)
        assert resp.code == 0, f"创建商品失败: {resp.msg}"
        return resp.data["id"]

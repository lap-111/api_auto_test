"""全局 pytest 配置与 fixture"""
import uuid

import pytest

from api import AdminApi, CartApi, OrderApi, ProductApi, UserApi
from core.config import Config
from core.factory import Factory
from core.http_client import HttpClient


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev", help="指定测试环境: dev/test")


@pytest.fixture(scope="session")
def config(request):
    """环境配置：读取 --env 参数对应的 YAML 配置"""
    return Config(request.config.getoption("--env"))


@pytest.fixture(scope="session")
def client(config):
    """HTTP 请求客户端"""
    return HttpClient(config)


@pytest.fixture(scope="session")
def user_api(client):
    return UserApi(client)


@pytest.fixture(scope="session")
def product_api(client):
    return ProductApi(client)


@pytest.fixture(scope="session")
def cart_api(client):
    return CartApi(client)


@pytest.fixture(scope="session")
def order_api(client):
    return OrderApi(client)


@pytest.fixture(scope="session")
def admin_api(client):
    return AdminApi(client)


@pytest.fixture
def factory(user_api, admin_api, product_api, cart_api, order_api):
    """场景用例数据工厂：造数与多用户登录态切换"""
    return Factory(user_api, admin_api, product_api, cart_api, order_api)


@pytest.fixture
def auth_client(client, user_api):
    """创建独立随机用户并登录，将 token 注入 client；用例结束后清除（保证数据隔离）"""
    username = f"auto_{uuid.uuid4().hex[:8]}"
    user_api.register(username=username, password="abc123")
    resp = user_api.login(username=username, password="abc123")
    client.set_token(resp.data["token"])
    yield client
    client.set_token(None)


@pytest.fixture
def admin_client(client, admin_api):
    """管理员登录并注入 token"""
    resp = admin_api.login("admin", "admin123")
    client.set_token(resp.data["token"])
    yield client
    client.set_token(None)

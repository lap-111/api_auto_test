"""全局 pytest 配置与 fixture"""
import pytest

from core.config import Config
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

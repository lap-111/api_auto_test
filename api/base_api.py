"""接口对象基类"""
from core.logger import get_logger


class BaseApi:
    """所有接口对象的基类：持有请求客户端"""

    def __init__(self, client):
        self.client = client
        self.logger = get_logger("api")

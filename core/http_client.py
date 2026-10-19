"""HTTP 请求封装：基于 requests.Session，统一响应解析、token 注入、超时与重试、请求日志"""
import time

import requests

from .logger import get_logger


class ApiResponse:
    """统一响应包装：暴露 HTTP 状态码与业务 code/msg/data"""

    def __init__(self, resp):
        self.http_status = resp.status_code
        self._raw = resp
        try:
            self.body = resp.json()
        except ValueError:
            self.body = None

    @property
    def code(self):
        return self.body.get("code") if isinstance(self.body, dict) else None

    @property
    def msg(self):
        return self.body.get("msg") if isinstance(self.body, dict) else None

    @property
    def data(self):
        return self.body.get("data") if isinstance(self.body, dict) else None

    def json(self):
        return self.body


class HttpClient:
    """请求客户端：管理 Session 与登录态 token"""

    def __init__(self, config):
        self.base_url = config.base_url
        self.timeout = config.timeout
        self.session = requests.Session()
        self.logger = get_logger("http")
        self.token = None

    def set_token(self, token):
        """设置登录态 token，后续请求自动携带"""
        self.token = token

    def _headers(self, headers=None):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if headers:
            h.update(headers)
        return h

    def request(self, method, url, retry=0, **kwargs):
        full_url = url if url.startswith("http") else self.base_url + url
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", self.timeout)

        for attempt in range(retry + 1):
            try:
                self.logger.info(
                    f"[{method}] {full_url} params={kwargs.get('params')} json={kwargs.get('json')}")
                resp = self.session.request(method, full_url, **kwargs)
                self.logger.info(f"<- {resp.status_code} {resp.text[:500]}")
                if resp.status_code < 500:  # 5xx 才重试
                    return ApiResponse(resp)
            except requests.RequestException as e:
                self.logger.warning(f"[{method}] {full_url} 请求异常: {e}")
            if attempt < retry:
                self.logger.info(f"第 {attempt + 1} 次重试: {full_url}")
                time.sleep(0.5 * (attempt + 1))

        raise requests.RequestException(f"[{method}] {full_url} 请求失败")

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

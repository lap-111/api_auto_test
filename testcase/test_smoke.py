"""P1 冒烟用例：验证框架骨架（请求封装/断言工具/配置）可正常跑通接口"""
import allure
import pytest

from core.assert_utils import assert_code, assert_data_field, assert_field_exists, assert_http_status, assert_ok

pytestmark = pytest.mark.smoke


@allure.feature("冒烟")
@allure.story("框架骨架")
def test_health(client):
    """健康检查：验证 GET 请求与断言工具链路"""
    resp = client.get("/api/health")
    assert_http_status(resp, 200)
    assert_ok(resp)
    assert_data_field(resp, "status", "ok")


@allure.feature("冒烟")
@allure.story("框架骨架")
def test_login_success(client):
    """登录成功：验证 JSON 请求体、响应解析与 token 提取"""
    resp = client.post("/api/users/login", json={"username": "user01", "password": "123456"})
    assert_http_status(resp, 200)
    assert_ok(resp)
    assert_field_exists(resp, "token")
    assert_data_field(resp, "user.username", "user01")
    assert_data_field(resp, "user.role", "user")


@allure.feature("冒烟")
@allure.story("框架骨架")
def test_login_wrong_password(client):
    """登录失败：验证错误码断言"""
    resp = client.post("/api/users/login", json={"username": "user01", "password": "wrong-pass"})
    assert_http_status(resp, 200)
    assert_code(resp, 2003)

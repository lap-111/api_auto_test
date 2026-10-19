"""用户模块单接口用例"""
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_http_status, assert_ok)
from helpers import random_username

pytestmark = pytest.mark.regression


class TestRegister:

    def test_register_duplicate(self, user_api):
        """重复注册返回 2001（两步操作，不适合表格化）"""
        username = random_username()
        assert_ok(user_api.register(username, "abc123"))
        resp = user_api.register(username, "abc123")
        assert_code(resp, 2001)

    def test_register_min_length_success(self, user_api):
        """边界值：3 位用户名可注册成功"""
        assert_ok(user_api.register(random_username(prefix="", length=3), "abc123"))


class TestGetMe:

    def test_get_me_success(self, auth_client, user_api):
        """正向：获取当前用户信息"""
        resp = user_api.get_me()
        assert_ok(resp)
        assert_field_exists(resp, "username")
        assert_data_field(resp, "role", "user")

    def test_get_me_unauthorized(self, client, user_api):
        """未授权：无 token 返回 401/1002"""
        client.set_token(None)
        resp = user_api.get_me()
        assert_http_status(resp, 401)
        assert_code(resp, 1002)

    def test_get_me_invalid_token(self, client, user_api):
        """未授权：伪造 token 返回 401/1002"""
        client.set_token("invalid.token.abc")
        resp = user_api.get_me()
        assert_http_status(resp, 401)
        assert_code(resp, 1002)


class TestUpdateMe:

    def test_update_me_success(self, auth_client, user_api):
        """正向：修改昵称"""
        resp = user_api.update_me("新昵称")
        assert_ok(resp)
        assert_data_field(resp, "nickname", "新昵称")

    def test_update_me_missing_param(self, auth_client, user_api):
        """参数缺失返回 400/1001"""
        resp = user_api.update_me("")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_update_me_unauthorized(self, client, user_api):
        """未授权返回 401/1002"""
        client.set_token(None)
        resp = user_api.update_me("昵称")
        assert_http_status(resp, 401)
        assert_code(resp, 1002)

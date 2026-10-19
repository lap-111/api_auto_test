"""用户模块单接口用例"""
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_http_status, assert_ok)
from helpers import random_username

pytestmark = pytest.mark.regression


class TestRegister:

    def test_register_success(self, user_api):
        """正向：注册成功返回用户信息"""
        resp = user_api.register(random_username(), "abc123")
        assert_ok(resp)
        assert_field_exists(resp, "id")
        assert_data_field(resp, "balance", 10000)
        assert_data_field(resp, "role", "user")

    def test_register_duplicate(self, user_api):
        """重复注册返回 2001"""
        username = random_username()
        assert_ok(user_api.register(username, "abc123"))
        resp = user_api.register(username, "abc123")
        assert_code(resp, 2001)

    def test_register_missing_params(self, user_api):
        """参数缺失返回 400/1001"""
        resp = user_api.register("", "")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_register_username_boundary(self, user_api):
        """边界值：3 位用户名通过，21 位拒绝"""
        assert_ok(user_api.register(random_username(prefix="", length=3), "abc123"))
        resp = user_api.register(random_username(prefix="", length=21), "abc123")
        assert_code(resp, 1001)

    def test_register_password_too_short(self, user_api):
        """边界值：5 位密码拒绝"""
        resp = user_api.register(random_username(), "12345")
        assert_code(resp, 1001)

    def test_register_type_error(self, user_api):
        """类型错误：username 传数字返回 400/1001"""
        resp = user_api.register(12345, "abc123")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)


class TestLogin:

    def test_login_success(self, user_api):
        """正向：登录返回 token 与用户信息"""
        username = random_username()
        assert_ok(user_api.register(username, "abc123"))
        resp = user_api.login(username, "abc123")
        assert_ok(resp)
        assert_field_exists(resp, "token")
        assert_data_field(resp, "user.username", username)

    def test_login_wrong_password(self, user_api):
        """密码错误返回 2003"""
        username = random_username()
        assert_ok(user_api.register(username, "abc123"))
        resp = user_api.login(username, "wrong-pass")
        assert_code(resp, 2003)

    def test_login_user_not_found(self, user_api):
        """用户不存在返回 2002"""
        resp = user_api.login("nobody_exists", "abc123")
        assert_code(resp, 2002)

    def test_login_missing_params(self, user_api):
        """参数缺失返回 400/1001"""
        resp = user_api.login("", "")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_login_type_error(self, user_api):
        """类型错误：password 传数字返回 400/1001"""
        resp = user_api.login("user01", 123456)
        assert_http_status(resp, 400)
        assert_code(resp, 1001)


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

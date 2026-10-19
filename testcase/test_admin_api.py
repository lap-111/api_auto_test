"""后台管理模块单接口用例"""
import allure
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_http_status, assert_ok)
from helpers import random_username

pytestmark = pytest.mark.regression


@allure.feature("后台管理")
@allure.story("管理员登录")
class TestAdminLogin:

    def test_login_success(self, admin_api):
        """正向：管理员登录"""
        resp = admin_api.login("admin", "admin123")
        assert_ok(resp)
        assert_field_exists(resp, "token")
        assert_data_field(resp, "user.role", "admin")

    def test_login_wrong_password(self, admin_api):
        """密码错误返回 1003"""
        resp = admin_api.login("admin", "wrong-pass")
        assert_code(resp, 1003)

    def test_login_normal_user_forbidden(self, admin_api):
        """普通用户调后台登录返回 1003"""
        resp = admin_api.login("user01", "123456")
        assert_code(resp, 1003)


@allure.feature("后台管理")
@allure.story("新增商品")
class TestCreateProduct:

    def test_create_success(self, admin_client, admin_api):
        """正向：新增商品"""
        resp = admin_api.create_product(name="测试商品A", price=9.9, stock=10, category="测试")
        assert_ok(resp)
        assert_field_exists(resp, "id")
        assert_data_field(resp, "status", "on")

    def test_create_missing_params(self, admin_client, admin_api):
        """参数缺失返回 400/1001"""
        resp = admin_api.create_product(name="", price=1, stock=1, category="测试")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_create_invalid_price(self, admin_client, admin_api):
        """边界值/类型错误：price=0 或字符串返回 400/1001"""
        resp = admin_api.create_product(name="x", price=0, stock=1, category="测试")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)
        resp = admin_api.create_product(name="x", price="abc", stock=1, category="测试")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_create_invalid_stock(self, admin_client, admin_api):
        """边界值：stock 为负返回 400/1001"""
        resp = admin_api.create_product(name="x", price=1, stock=-1, category="测试")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_create_type_error(self, admin_client, admin_api):
        """类型错误：name 传数字返回 400/1001"""
        resp = admin_api.create_product(name=123, price=1, stock=1, category="测试")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_create_unauthorized(self, client, admin_api):
        """未授权返回 401/1002"""
        client.set_token(None)
        resp = admin_api.create_product(name="x", price=1, stock=1, category="测试")
        assert_http_status(resp, 401)
        assert_code(resp, 1002)

    def test_create_forbidden(self, auth_client, admin_api):
        """普通用户无权限返回 403/1003"""
        resp = admin_api.create_product(name="x", price=1, stock=1, category="测试")
        assert_http_status(resp, 403)
        assert_code(resp, 1003)


@allure.feature("后台管理")
@allure.story("上下架")
class TestUpdateStatus:

    def test_off_shelf_success(self, admin_client, admin_api):
        """正向：下架商品"""
        pid = admin_api.create_product(name="上架测试", price=1, stock=1, category="测试").data["id"]
        resp = admin_api.update_status(pid, "off")
        assert_ok(resp)
        assert_data_field(resp, "status", "off")

    def test_update_status_not_found(self, admin_client, admin_api):
        """商品不存在返回 3001"""
        resp = admin_api.update_status(999999, "off")
        assert_code(resp, 3001)

    def test_update_status_invalid_value(self, admin_client, admin_api):
        """非法状态值返回 400/1001"""
        pid = admin_api.create_product(name="状态测试", price=1, stock=1, category="测试").data["id"]
        resp = admin_api.update_status(pid, "xxx")
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_update_status_forbidden(self, auth_client, admin_api):
        """普通用户无权限返回 403/1003"""
        resp = admin_api.update_status(1, "off")
        assert_http_status(resp, 403)
        assert_code(resp, 1003)

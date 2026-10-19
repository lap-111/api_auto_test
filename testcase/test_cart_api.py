"""购物车模块单接口用例"""
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_http_status, assert_length, assert_ok)
from helpers import random_username

pytestmark = pytest.mark.regression


class TestAddItem:

    def test_add_unauthorized(self, client, cart_api):
        """未授权返回 401/1002"""
        client.set_token(None)
        resp = cart_api.add_item(product_id=5, quantity=1)
        assert_http_status(resp, 401)
        assert_code(resp, 1002)

    def test_add_off_shelf_product(self, auth_client, cart_api, admin_api):
        """已下架商品加购返回 3002（多步交互场景）"""
        user_token = auth_client.token
        resp = admin_api.login("admin", "admin123")
        auth_client.set_token(resp.data["token"])
        pid = admin_api.create_product(name=random_username(), price=9.9, stock=5, category="测试").data["id"]
        assert_ok(admin_api.update_status(pid, "off"))
        auth_client.set_token(user_token)
        resp = cart_api.add_item(product_id=pid, quantity=1)
        assert_code(resp, 3002)


class TestGetCart:

    def test_get_success(self, auth_client, cart_api):
        """正向：购物车列表含商品信息"""
        cart_api.add_item(product_id=5, quantity=1)
        cart_api.add_item(product_id=6, quantity=2)
        resp = cart_api.get_cart()
        assert_ok(resp)
        assert_length(resp, "items", 2)
        for item in resp.data["items"]:
            assert item["product_name"] and item["price"] and item["total"]

    def test_get_empty(self, auth_client, cart_api):
        """空购物车返回空列表"""
        resp = cart_api.get_cart()
        assert_ok(resp)
        assert_length(resp, "items", 0)

    def test_get_unauthorized(self, client, cart_api):
        """未授权返回 401/1002"""
        client.set_token(None)
        resp = cart_api.get_cart()
        assert_http_status(resp, 401)
        assert_code(resp, 1002)


class TestUpdateItem:

    def test_update_success(self, auth_client, cart_api):
        """正向：修改数量"""
        item_id = cart_api.add_item(product_id=5).data["id"]
        resp = cart_api.update_item(item_id, quantity=3)
        assert_ok(resp)
        assert_data_field(resp, "quantity", 3)

    def test_update_not_found(self, auth_client, cart_api):
        """购物车项不存在返回 4002"""
        resp = cart_api.update_item(999999, quantity=1)
        assert_code(resp, 4002)

    def test_update_invalid_quantity(self, auth_client, cart_api):
        """边界值：quantity=0 返回 400/1001"""
        item_id = cart_api.add_item(product_id=5).data["id"]
        resp = cart_api.update_item(item_id, quantity=0)
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_update_unauthorized(self, client, cart_api):
        """未授权返回 401/1002"""
        client.set_token(None)
        resp = cart_api.update_item(1, quantity=2)
        assert_http_status(resp, 401)
        assert_code(resp, 1002)


class TestRemoveItem:

    def test_remove_success(self, auth_client, cart_api):
        """正向：删除后购物车为空"""
        item_id = cart_api.add_item(product_id=5).data["id"]
        assert_ok(cart_api.remove_item(item_id))
        assert_length(cart_api.get_cart(), "items", 0)

    def test_remove_not_found(self, auth_client, cart_api):
        """购物车项不存在返回 4002"""
        resp = cart_api.remove_item(999999)
        assert_code(resp, 4002)

    def test_remove_unauthorized(self, client, cart_api):
        """未授权返回 401/1002"""
        client.set_token(None)
        resp = cart_api.remove_item(1)
        assert_http_status(resp, 401)
        assert_code(resp, 1002)

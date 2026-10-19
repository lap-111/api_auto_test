"""订单模块单接口用例"""
import allure
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_greater, assert_http_status, assert_length, assert_ok)
from helpers import random_username

pytestmark = pytest.mark.regression


def _add_and_order(cart_api, order_api, product_id=5, quantity=1):
    """加购并下单，返回订单响应"""
    cart_api.add_item(product_id=product_id, quantity=quantity)
    return order_api.create_order()


@allure.feature("订单模块")
@allure.story("下单")
class TestCreateOrder:

    def test_create_success(self, auth_client, cart_api, order_api):
        """正向：下单生成 pending 订单并清空购物车"""
        cart_api.add_item(product_id=5, quantity=1)
        cart_api.add_item(product_id=6, quantity=1)
        resp = order_api.create_order()
        assert_ok(resp)
        assert_data_field(resp, "status", "pending")
        assert_field_exists(resp, "order_no")
        items = resp.data["items"]
        assert len(items) == 2 and items[0]["product_name"]
        assert_length(cart_api.get_cart(), "items", 0)

    def test_create_empty_cart(self, auth_client, order_api):
        """空购物车下单返回 4001"""
        resp = order_api.create_order()
        assert_code(resp, 4001)

    def test_create_unauthorized(self, client, order_api):
        """未授权返回 401/1002"""
        client.set_token(None)
        resp = order_api.create_order()
        assert_http_status(resp, 401)
        assert_code(resp, 1002)

    def test_create_selected_items(self, auth_client, cart_api, order_api):
        """指定 cart_item_ids 只对选中项下单"""
        item_a = cart_api.add_item(product_id=5).data["id"]
        cart_api.add_item(product_id=6)
        resp = order_api.create_order(cart_item_ids=[item_a])
        assert_ok(resp)
        assert len(resp.data["items"]) == 1
        assert resp.data["items"][0]["product_id"] == 5

    def test_create_cart_item_ids_type_error(self, auth_client, order_api):
        """类型错误：cart_item_ids 传整数返回 400/1001"""
        resp = order_api.create_order(cart_item_ids=5)
        assert_http_status(resp, 400)
        assert_code(resp, 1001)

    def test_create_stock_not_enough(self, auth_client, cart_api, order_api, admin_api):
        """库存不足：他人下单耗尽库存后，本用户下单失败返回 3003（结束后取消恢复库存）"""
        user_token = auth_client.token
        cart_api.add_item(product_id=4, quantity=20)
        resp = admin_api.login("admin", "admin123")
        auth_client.set_token(resp.data["token"])
        cart_api.add_item(product_id=4, quantity=20)
        admin_order_id = order_api.create_order().data["id"]
        auth_client.set_token(user_token)
        resp = order_api.create_order()
        assert_code(resp, 3003)
        # 清理：管理员取消订单，恢复商品 4 库存
        resp = admin_api.login("admin", "admin123")
        auth_client.set_token(resp.data["token"])
        assert_ok(order_api.cancel_order(admin_order_id))
        auth_client.set_token(user_token)


@allure.feature("订单模块")
@allure.story("订单列表")
class TestListOrders:

    def test_list_success(self, auth_client, cart_api, order_api):
        """正向：订单列表分页返回"""
        _add_and_order(cart_api, order_api)
        resp = order_api.list_orders()
        assert_ok(resp)
        assert_greater(resp, "total", 0)
        for order in resp.data["items"]:
            assert order["status"] and order["order_no"]

    def test_list_empty(self, auth_client, order_api):
        """新用户无订单"""
        resp = order_api.list_orders()
        assert_ok(resp)
        assert_data_field(resp, "total", 0)
        assert_length(resp, "items", 0)


@allure.feature("订单模块")
@allure.story("订单详情")
class TestGetOrder:

    def test_get_success(self, auth_client, cart_api, order_api):
        """正向：订单详情"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        resp = order_api.get_order(order_id)
        assert_ok(resp)
        assert_data_field(resp, "status", "pending")
        assert_field_exists(resp, "order_no")

    def test_get_not_found(self, auth_client, order_api):
        """订单不存在返回 5001"""
        resp = order_api.get_order(999999)
        assert_code(resp, 5001)

    def test_get_other_user_order(self, auth_client, cart_api, order_api, user_api):
        """越权：他人订单不可见返回 5001"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        token = auth_client.token
        username = random_username()
        assert_ok(user_api.register(username, "abc123"))
        other_token = user_api.login(username, "abc123").data["token"]
        auth_client.set_token(other_token)
        resp = order_api.get_order(order_id)
        assert_code(resp, 5001)
        auth_client.set_token(token)


@allure.feature("订单模块")
@allure.story("支付")
class TestPayOrder:

    def test_pay_success(self, auth_client, cart_api, order_api, user_api):
        """正向：支付后状态 paid 且余额扣减"""
        order_id = _add_and_order(cart_api, order_api, product_id=5).data["id"]
        resp = order_api.pay_order(order_id)
        assert_ok(resp)
        assert_data_field(resp, "status", "paid")
        assert_field_exists(resp, "paid_at")
        assert user_api.get_me().data["balance"] == 10000 - 249

    def test_pay_repeat(self, auth_client, cart_api, order_api):
        """重复支付返回 5004"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        assert_ok(order_api.pay_order(order_id))
        resp = order_api.pay_order(order_id)
        assert_code(resp, 5004)

    def test_pay_insufficient_balance(self, auth_client, cart_api, order_api):
        """余额不足返回 5003（结束后取消订单恢复库存）"""
        cart_api.add_item(product_id=1, quantity=2)  # 7999*2=15998 > 10000
        order_id = order_api.create_order().data["id"]
        resp = order_api.pay_order(order_id)
        assert_code(resp, 5003)
        assert_ok(order_api.cancel_order(order_id))

    def test_pay_canceled_order(self, auth_client, cart_api, order_api):
        """已取消订单支付返回 5002"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        assert_ok(order_api.cancel_order(order_id))
        resp = order_api.pay_order(order_id)
        assert_code(resp, 5002)

    def test_pay_not_found(self, auth_client, order_api):
        """订单不存在返回 5001"""
        resp = order_api.pay_order(999999)
        assert_code(resp, 5001)


@allure.feature("订单模块")
@allure.story("取消")
class TestCancelOrder:

    def test_cancel_success(self, auth_client, cart_api, order_api, product_api):
        """正向：取消后状态 canceled 且库存返还"""
        stock_before = product_api.get_product(2).data["stock"]
        order_id = _add_and_order(cart_api, order_api, product_id=2).data["id"]
        resp = order_api.cancel_order(order_id)
        assert_ok(resp)
        assert_data_field(resp, "status", "canceled")
        assert product_api.get_product(2).data["stock"] == stock_before

    def test_cancel_paid_order(self, auth_client, cart_api, order_api):
        """已支付订单不可取消返回 5002"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        assert_ok(order_api.pay_order(order_id))
        resp = order_api.cancel_order(order_id)
        assert_code(resp, 5002)

    def test_cancel_completed_order(self, auth_client, cart_api, order_api):
        """已完成订单不可取消返回 5002"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        assert_ok(order_api.pay_order(order_id))
        assert_ok(order_api.confirm_order(order_id))
        resp = order_api.cancel_order(order_id)
        assert_code(resp, 5002)


@allure.feature("订单模块")
@allure.story("确认收货")
class TestConfirmOrder:

    def test_confirm_success(self, auth_client, cart_api, order_api):
        """正向：确认收货后状态 completed"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        assert_ok(order_api.pay_order(order_id))
        resp = order_api.confirm_order(order_id)
        assert_ok(resp)
        assert_data_field(resp, "status", "completed")

    def test_confirm_pending_order(self, auth_client, cart_api, order_api):
        """待支付订单确认收货返回 5002"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        resp = order_api.confirm_order(order_id)
        assert_code(resp, 5002)

    def test_confirm_repeat(self, auth_client, cart_api, order_api):
        """重复确认收货返回 5002"""
        order_id = _add_and_order(cart_api, order_api).data["id"]
        assert_ok(order_api.pay_order(order_id))
        assert_ok(order_api.confirm_order(order_id))
        resp = order_api.confirm_order(order_id)
        assert_code(resp, 5002)

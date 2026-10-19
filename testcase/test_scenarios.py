"""全链路场景用例：完整购物流程、订单状态机、多用户隔离、支付与下架场景"""
import pytest

from core.assert_utils import assert_code, assert_ok
from core.factory import TokenSwitch


class TestBuyFlow:
    """核心购物链路（冒烟）"""

    pytestmark = pytest.mark.smoke

    def test_complete_shopping_flow(self, factory, client):
        """完整购物流程：注册→登录→搜索→加购→下单→支付→确认收货"""
        user = factory.create_user()
        with TokenSwitch(client, user["token"]):
            # 搜索商品
            resp = factory.product_api.list_products(keyword="罗技")
            assert_ok(resp)
            assert resp.data["items"], "未搜到罗技商品"
            pid = resp.data["items"][0]["id"]
            assert resp.data["items"][0]["price"] == 249

            # 加购 2 件并校验购物车
            assert_ok(factory.cart_api.add_item(pid, quantity=2))
            cart = factory.cart_api.get_cart().data["items"]
            assert len(cart) == 1 and cart[0]["quantity"] == 2

            # 下单：金额 = 249*2
            order = factory.order_api.create_order().data
            assert order["status"] == "pending"
            assert order["total_amount"] == 498
            assert len(order["items"]) == 1

            # 下单后购物车清空
            assert factory.cart_api.get_cart().data["items"] == []

            # 支付：状态 paid、余额扣减
            pay = factory.order_api.pay_order(order["id"])
            assert_ok(pay)
            assert pay.data["status"] == "paid"
            assert factory.user_api.get_me().data["balance"] == 10000 - 498

            # 确认收货：completed
            confirm = factory.order_api.confirm_order(order["id"])
            assert_ok(confirm)
            assert confirm.data["status"] == "completed"


class TestOrderStateMachine:
    """订单状态机流转（回归）"""

    pytestmark = pytest.mark.regression

    def test_state_flow_pending_to_completed(self, factory, client):
        """pending -> paid -> completed 全流程，终态不可再操作"""
        user = factory.create_user()
        with TokenSwitch(client, user["token"]):
            factory.cart_api.add_item(5, 1)
            order_id = factory.order_api.create_order().data["id"]
            assert factory.order_api.get_order(order_id).data["status"] == "pending"
            assert factory.order_api.confirm_order(order_id).code == 5002  # pending 不可确认

            assert factory.order_api.pay_order(order_id).data["status"] == "paid"
            assert factory.order_api.cancel_order(order_id).code == 5002   # paid 不可取消

            assert factory.order_api.confirm_order(order_id).data["status"] == "completed"
            assert factory.order_api.pay_order(order_id).code == 5002      # completed 不可支付
            assert factory.order_api.confirm_order(order_id).code == 5002  # 重复确认

    def test_paid_order_cannot_pay_again(self, factory, client):
        """重复支付返回 5004"""
        user = factory.create_user()
        with TokenSwitch(client, user["token"]):
            factory.cart_api.add_item(5, 1)
            order_id = factory.order_api.create_order().data["id"]
            assert_ok(factory.order_api.pay_order(order_id))
            assert_code(factory.order_api.pay_order(order_id), 5004)

    def test_canceled_order_cannot_pay(self, factory, client):
        """已取消订单支付返回 5002"""
        user = factory.create_user()
        with TokenSwitch(client, user["token"]):
            factory.cart_api.add_item(5, 1)
            order_id = factory.order_api.create_order().data["id"]
            assert_ok(factory.order_api.cancel_order(order_id))
            assert_code(factory.order_api.pay_order(order_id), 5002)

    def test_cancel_restores_stock(self, factory, client):
        """取消订单后库存返还"""
        stock_before = factory.product_api.get_product(5).data["stock"]
        user = factory.create_user()
        with TokenSwitch(client, user["token"]):
            factory.cart_api.add_item(5, 1)
            order_id = factory.order_api.create_order().data["id"]
            resp = factory.order_api.cancel_order(order_id)
            assert_ok(resp)
            assert resp.data["status"] == "canceled"
            assert factory.product_api.get_product(5).data["stock"] == stock_before


class TestMultiUser:
    """多用户数据隔离与越权（回归）"""

    pytestmark = pytest.mark.regression

    def test_two_users_isolated(self, factory, client):
        """两个用户各自下单互不干扰，且互相不可见对方订单"""
        u1 = factory.create_user()
        u2 = factory.create_user()

        with TokenSwitch(client, u1["token"]):
            factory.cart_api.add_item(5, 1)
            o1 = factory.order_api.create_order().data["id"]
        with TokenSwitch(client, u2["token"]):
            factory.cart_api.add_item(6, 1)
            o2_order = factory.order_api.create_order().data
            o2 = o2_order["id"]
            # 订单互不干扰：u2 的订单只含商品 6
            assert len(o2_order["items"]) == 1
            assert o2_order["items"][0]["product_id"] == 6
            # 越权：看不到 u1 的订单
            assert_code(factory.order_api.get_order(o1), 5001)
        with TokenSwitch(client, u1["token"]):
            assert_code(factory.order_api.get_order(o2), 5001)
            assert factory.order_api.get_order(o1).data["items"][0]["product_id"] == 5


class TestPayment:
    """支付边界场景（回归）"""

    pytestmark = pytest.mark.regression

    def test_insufficient_balance(self, factory, client):
        """余额不足支付失败，取消订单恢复库存"""
        user = factory.create_user()
        with TokenSwitch(client, user["token"]):
            factory.cart_api.add_item(1, 2)  # 7999*2=15998 > 10000
            order_id = factory.order_api.create_order().data["id"]
            assert_code(factory.order_api.pay_order(order_id), 5003)
            assert_ok(factory.order_api.cancel_order(order_id))


class TestOffShelf:
    """商品上下架对购买链路的影响（回归）"""

    pytestmark = pytest.mark.regression

    def test_off_shelf_blocks_purchase(self, factory, client):
        """下架商品无法加购"""
        user = factory.create_user()
        with TokenSwitch(client, factory.admin_login()):
            pid = factory.create_product()
            assert_ok(factory.admin_api.update_status(pid, "off"))
        with TokenSwitch(client, user["token"]):
            assert_code(factory.cart_api.add_item(pid, 1), 3002)

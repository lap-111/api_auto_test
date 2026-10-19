"""订单模块接口对象"""


class OrderApi:

    def __init__(self, client):
        self.client = client

    def create_order(self, cart_item_ids=None):
        """下单（默认全部购物车项）"""
        data = {}
        if cart_item_ids is not None:
            data["cart_item_ids"] = cart_item_ids
        return self.client.post("/api/orders", json=data)

    def list_orders(self, page=1, page_size=10):
        """订单列表"""
        return self.client.get("/api/orders", params={"page": page, "page_size": page_size})

    def get_order(self, order_id):
        """订单详情"""
        return self.client.get(f"/api/orders/{order_id}")

    def cancel_order(self, order_id):
        """取消订单"""
        return self.client.post(f"/api/orders/{order_id}/cancel")

    def pay_order(self, order_id):
        """支付订单"""
        return self.client.post(f"/api/orders/{order_id}/pay")

    def confirm_order(self, order_id):
        """确认收货"""
        return self.client.post(f"/api/orders/{order_id}/confirm")

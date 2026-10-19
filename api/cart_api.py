"""购物车模块接口对象"""
from .base_api import BaseApi


class CartApi(BaseApi):

    def add_item(self, product_id, quantity=1):
        """加购"""
        return self.client.post("/api/cart/items", json={"product_id": product_id, "quantity": quantity})

    def get_cart(self):
        """查看购物车"""
        return self.client.get("/api/cart")

    def update_item(self, item_id, quantity):
        """修改数量"""
        return self.client.put(f"/api/cart/items/{item_id}", json={"quantity": quantity})

    def remove_item(self, item_id):
        """删除购物车项"""
        return self.client.delete(f"/api/cart/items/{item_id}")

"""后台管理接口对象"""
from .base_api import BaseApi


class AdminApi(BaseApi):

    def login(self, username, password):
        """管理员登录"""
        return self.client.post("/api/admin/login", json={"username": username, "password": password})

    def create_product(self, name, price, stock, category, description=""):
        """新增商品"""
        return self.client.post("/api/admin/products", json={
            "name": name, "price": price, "stock": stock,
            "category": category, "description": description,
        })

    def update_status(self, product_id, status):
        """上架(on)/下架(off)"""
        return self.client.put(f"/api/admin/products/{product_id}/status", json={"status": status})

"""商品模块接口对象"""
from .base_api import BaseApi


class ProductApi(BaseApi):

    def list_products(self, page=1, page_size=10, category=None, keyword=None):
        """商品列表（分页/分类/搜索）"""
        params = {"page": page, "page_size": page_size}
        if category:
            params["category"] = category
        if keyword:
            params["keyword"] = keyword
        return self.client.get("/api/products", params=params)

    def get_product(self, product_id):
        """商品详情"""
        return self.client.get(f"/api/products/{product_id}")

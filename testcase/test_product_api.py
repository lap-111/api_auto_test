"""商品模块单接口用例"""
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_greater, assert_http_status, assert_length, assert_ok)

pytestmark = pytest.mark.regression


class TestListProducts:

    def test_list_success(self, product_api):
        """正向：默认分页返回商品列表"""
        resp = product_api.list_products()
        assert_ok(resp)
        assert_greater(resp, "total", 9)
        assert_field_exists(resp, "items")
        for item in resp.data["items"]:
            assert "id" in item and "name" in item and "price" in item

    def test_list_pagination(self, product_api):
        """分页：page_size=5 返回 5 条"""
        resp = product_api.list_products(page=1, page_size=5)
        assert_ok(resp)
        assert_data_field(resp, "page", 1)
        assert_data_field(resp, "page_size", 5)
        assert_length(resp, "items", 5)

    def test_list_page_overflow(self, product_api):
        """边界值：超大页码返回空列表"""
        resp = product_api.list_products(page=999)
        assert_ok(resp)
        assert_length(resp, "items", 0)

    def test_list_page_zero_clamped(self, product_api):
        """边界值：page=0 被约束为 1"""
        resp = product_api.list_products(page=0)
        assert_ok(resp)
        assert_data_field(resp, "page", 1)

    def test_list_negative_page_size_clamped(self, product_api):
        """边界值：page_size=-1 被约束为 1"""
        resp = product_api.list_products(page=1, page_size=-1)
        assert_ok(resp)
        assert_data_field(resp, "page_size", 1)

    def test_list_keyword(self, product_api):
        """搜索：关键字命中"""
        resp = product_api.list_products(keyword="iPhone")
        assert_ok(resp)
        assert_greater(resp, "total", 0)
        for item in resp.data["items"]:
            assert "iPhone" in item["name"]

    def test_list_keyword_no_match(self, product_api):
        """搜索：无命中返回空"""
        resp = product_api.list_products(keyword="不存在商品xyz")
        assert_ok(resp)
        assert_data_field(resp, "total", 0)
        assert_length(resp, "items", 0)

    def test_list_category(self, product_api):
        """分类筛选：命中"""
        resp = product_api.list_products(category="手机")
        assert_ok(resp)
        assert_greater(resp, "total", 1)

    def test_list_category_no_match(self, product_api):
        """分类筛选：不存在分类返回空"""
        resp = product_api.list_products(category="不存在分类")
        assert_ok(resp)
        assert_data_field(resp, "total", 0)


class TestGetProduct:

    def test_get_success(self, product_api):
        """正向：商品详情"""
        resp = product_api.get_product(1)
        assert_ok(resp)
        assert_data_field(resp, "id", 1)
        assert_data_field(resp, "name", "iPhone 15 Pro")
        assert_field_exists(resp, "stock")

    def test_get_not_found(self, product_api):
        """商品不存在返回 3001"""
        resp = product_api.get_product(999999)
        assert_code(resp, 3001)

    def test_get_invalid_id_type(self, client):
        """类型错误：非整数 ID 返回 404"""
        resp = client.get("/api/products/abc")
        assert_http_status(resp, 404)

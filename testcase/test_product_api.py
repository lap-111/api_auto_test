"""商品模块单接口用例"""
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_http_status, assert_ok)

pytestmark = pytest.mark.regression


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

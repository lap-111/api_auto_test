"""数据驱动用例：参数从 data/*.yaml 加载，用例数据与代码分离"""
import pytest

from core.assert_utils import (assert_code, assert_data_field, assert_field_exists,
                               assert_greater, assert_http_status, assert_length)
from core.data_loader import cases_path, load_cases, resolve_data


def _assert_case(resp, expect):
    """按用例 expect 配置执行断言：
    status=HTTP 状态码, code=业务码, msg=消息包含, data_eq=字段相等,
    data_not_null=字段非空, data_length=字段长度, data_gt=字段大于
    """
    if "status" in expect:
        assert_http_status(resp, expect["status"])
    if "code" in expect:
        assert_code(resp, expect["code"])
    if "msg" in expect:
        assert expect["msg"] in resp.msg, f"msg 不含期望值: {expect['msg']!r}, 实际: {resp.msg!r}"
    for field, value in (expect.get("data_eq") or {}).items():
        assert_data_field(resp, field, value)
    for field in expect.get("data_not_null") or []:
        assert_field_exists(resp, field)
    for field, value in (expect.get("data_length") or {}).items():
        assert_length(resp, field, value)
    for field, value in (expect.get("data_gt") or {}).items():
        assert_greater(resp, field, value)


@pytest.mark.regression
class TestLoginData:

    @pytest.mark.parametrize("case", load_cases(cases_path("login.yaml")), ids=lambda c: c["name"])
    def test_login(self, user_api, case):
        body = resolve_data(case["request"])
        resp = user_api.login(body.get("username"), body.get("password"))
        _assert_case(resp, case["expect"])


@pytest.mark.regression
class TestRegisterData:

    @pytest.mark.parametrize("case", load_cases(cases_path("register.yaml")), ids=lambda c: c["name"])
    def test_register(self, user_api, case):
        body = resolve_data(case["request"])
        resp = user_api.register(body.get("username"), body.get("password"))
        _assert_case(resp, case["expect"])


@pytest.mark.regression
class TestProductListData:

    @pytest.mark.parametrize("case", load_cases(cases_path("product_list.yaml")), ids=lambda c: c["name"])
    def test_list(self, product_api, case):
        params = resolve_data(case.get("params") or {})
        resp = product_api.list_products(**params)
        _assert_case(resp, case["expect"])


@pytest.mark.regression
class TestCartAddData:

    @pytest.mark.parametrize("case", load_cases(cases_path("cart_add.yaml")), ids=lambda c: c["name"])
    def test_add_item(self, auth_client, cart_api, case):
        body = resolve_data(case["request"])
        resp = cart_api.add_item(body.get("product_id"), body.get("quantity", 1))
        _assert_case(resp, case["expect"])

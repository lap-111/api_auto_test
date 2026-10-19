"""断言工具：统一断言 API 响应，失败时抛出带实际值的 AssertionError

字段路径支持点号，如 "user.username" 表示 data.user.username。
"""


def _get_path(data, path):
    """按点号路径取值，不存在返回 None"""
    for part in path.split("."):
        if isinstance(data, dict) and part in data:
            data = data[part]
        else:
            return None
    return data


def assert_http_status(resp, expected, msg=None):
    """断言 HTTP 状态码"""
    assert resp.http_status == expected, \
        f"HTTP 状态码不符: 期望={expected}, 实际={resp.http_status} {msg or ''}"


def assert_code(resp, expected, msg=None):
    """断言业务错误码 code"""
    assert resp.code == expected, \
        f"业务错误码不符: 期望={expected}, 实际={resp.code}({resp.msg}) {msg or ''}"


def assert_ok(resp, msg=None):
    """断言业务成功（code == 0）"""
    assert resp.code == 0, f"业务失败: code={resp.code}, msg={resp.msg} {msg or ''}"


def assert_field_exists(resp, field, msg=None):
    """断言 data 中存在指定字段（支持点号路径）"""
    assert _get_path(resp.data, field) is not None, \
        f"字段不存在: {field} {msg or ''}"


def assert_data_field(resp, field, expected, msg=None):
    """断言 data 中指定字段的值"""
    actual = _get_path(resp.data, field)
    assert actual == expected, \
        f"字段 {field} 不符: 期望={expected!r}, 实际={actual!r} {msg or ''}"


def assert_field_type(resp, field, expected_type, msg=None):
    """断言 data 中指定字段的类型"""
    actual = _get_path(resp.data, field)
    assert isinstance(actual, expected_type), \
        f"字段 {field} 类型不符: 期望={expected_type.__name__}, 实际={type(actual).__name__} {msg or ''}"


def assert_length(resp, field, expected, msg=None):
    """断言 data 中指定字段（列表/字符串）的长度"""
    actual = _get_path(resp.data, field)
    assert len(actual) == expected, \
        f"字段 {field} 长度不符: 期望={expected}, 实际={len(actual)} {msg or ''}"


def assert_greater(resp, field, value, msg=None):
    """断言 data 中指定字段大于某值"""
    actual = _get_path(resp.data, field)
    assert actual > value, \
        f"字段 {field} 应大于 {value}: 实际={actual} {msg or ''}"

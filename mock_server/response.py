"""统一响应结构与业务错误码"""


class Err:
    """业务错误码定义"""

    SUCCESS = 0            # 成功
    PARAM_ERROR = 1001     # 参数缺失 / 类型 / 格式错误（HTTP 400）
    UNAUTHORIZED = 1002    # 未登录或 token 无效 / 过期（HTTP 401）
    FORBIDDEN = 1003       # 无权限（HTTP 403）
    USER_EXISTS = 2001     # 用户名已存在
    USER_NOT_FOUND = 2002  # 用户不存在
    WRONG_PASSWORD = 2003  # 密码错误
    PRODUCT_NOT_FOUND = 3001  # 商品不存在
    PRODUCT_OFF_SHELF = 3002  # 商品已下架
    STOCK_NOT_ENOUGH = 3003   # 库存不足
    CART_EMPTY = 4001         # 购物车为空
    CART_ITEM_NOT_FOUND = 4002  # 购物车项不存在
    ORDER_NOT_FOUND = 5001    # 订单不存在
    ORDER_STATE_INVALID = 5002  # 订单状态不允许该操作
    BALANCE_NOT_ENOUGH = 5003   # 余额不足
    ORDER_ALREADY_PAID = 5004   # 订单已支付（重复支付）


def ok(data=None, msg="success"):
    """成功响应"""
    return {"code": Err.SUCCESS, "msg": msg, "data": data}


def fail(code, msg):
    """失败响应"""
    return {"code": code, "msg": msg, "data": None}

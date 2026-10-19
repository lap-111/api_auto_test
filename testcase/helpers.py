"""测试工具函数"""
import uuid


def random_username(prefix="auto", length=8):
    """生成随机用户名，避免跨用例/跨运行冲突"""
    return f"{prefix}_{uuid.uuid4().hex[:length]}" if prefix else uuid.uuid4().hex[:length]

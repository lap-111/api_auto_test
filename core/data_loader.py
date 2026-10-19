"""YAML 数据驱动：用例数据加载与占位符解析

占位符（在用例执行时解析，保证每次运行生成独立随机值）：
- {random_username}   随机用户名，如 auto_8f3a2b1c
- {random_hex:n}      随机 n 位十六进制字符串
"""
import os
import uuid

import yaml

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def cases_path(name):
    """拼接 data/ 目录下的用例文件路径"""
    return os.path.join(DATA_DIR, name)


def load_cases(path):
    """读取用例数据文件，返回用例列表（每条为 dict）"""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("cases", [])


def _resolve_placeholder(value):
    if not isinstance(value, str):
        return value
    if "{random_username}" in value:
        value = value.replace("{random_username}", f"auto_{uuid.uuid4().hex[:8]}")
    if "{random_hex:" in value:
        import re
        value = re.sub(r"\{random_hex:(\d+)\}", lambda m: uuid.uuid4().hex[:int(m.group(1))], value)
    return value


def resolve_data(obj):
    """递归解析对象中的占位符（每次调用生成独立随机值）"""
    if isinstance(obj, dict):
        return {k: resolve_data(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_data(item) for item in obj]
    return _resolve_placeholder(obj)

"""配置管理：读取 config/config.yaml，支持通过 pytest 参数 --env 切换环境"""
import os

import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "config.yaml")


class Config:
    """环境配置：base_url、超时、测试账号"""

    def __init__(self, env="dev"):
        self.env = env
        with open(CONFIG_PATH, encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}
        env_conf = self._data.get("envs", {}).get(env, {})
        self.base_url = env_conf.get("base_url")
        self.timeout = env_conf.get("timeout", 10)
        self.accounts = env_conf.get("accounts", {})

    def get(self, key, default=None):
        """读取顶层通用配置项"""
        return self._data.get(key, default)

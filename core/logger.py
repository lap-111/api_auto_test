"""日志模块：控制台 + 文件双输出"""
import logging
import os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

_loggers = {}


def get_logger(name="auto_test"):
    """获取（或创建）具名 logger，首次创建时配置控制台与文件输出"""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    if logger.handlers:  # 避免重复添加 handler
        _loggers[name] = logger
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    os.makedirs(LOG_DIR, exist_ok=True)
    fh = logging.FileHandler(os.path.join(LOG_DIR, f"test_{datetime.now():%Y%m%d}.log"),
                             encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    _loggers[name] = logger
    return logger

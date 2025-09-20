# app/middleware/logging.py
import logging
import sys

# 结构化日志
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# 添加控制台处理器（如果还没有的话）
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 防止日志重复输出
logger.propagate = False


import os
import re
from typing import List, Set

# 敏感词集合
_sensitive_words: Set[str] = set()


def load_sensitive_words(file_path: str = "sensitiveWord/sensitive_words_lines.txt"):
    """
    从文件加载敏感词列表
    """
    global _sensitive_words
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            _sensitive_words = {line.strip() for line in f if line.strip()}
    else:
        _sensitive_words = set()


def contains_sensitive_words(text: str) -> bool:
    """
    检查文本是否包含敏感词
    """
    for word in _sensitive_words:
        if word in text:
            return True
    return False


def filter_sensitive_words(text: str, replace_char: str = "*") -> str:
    """
    过滤敏感词，用指定字符替换
    """
    filtered_text = text
    for word in _sensitive_words:
        filtered_text = filtered_text.replace(word, replace_char * len(word))
    return filtered_text


def add_sensitive_word(word: str):
    """
    添加敏感词
    """
    global _sensitive_words
    _sensitive_words.add(word)


def remove_sensitive_word(word: str):
    """
    移除敏感词
    """
    global _sensitive_words
    _sensitive_words.discard(word)


# 初始化加载敏感词
load_sensitive_words()
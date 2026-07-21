"""
统一类型声明文件
定义所有 Cython 模块共享的类型和常量
"""

from libc.stdint cimport uint32_t, uint64_t

# 匹配结果结构
ctypedef struct MatchResult:
    uint32_t start
    uint32_t end
    uint32_t pattern_id

# 常量定义
DEF ALPHABET_SIZE = 256
DEF DEFAULT_BUFFER_SIZE = 1024

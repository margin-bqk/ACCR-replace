# 简化的 Matcher Cython 定义
# 移除了复杂的类型声明和 nogil 函数

from libc.stdint cimport uint32_t

# 简化的 Matcher 类定义
cdef class Matcher:
    cdef object ac_automaton
    cdef object regex_engine
    cdef object stream_buffer
    cdef bint streaming_mode
    cdef uint32_t total_matches
    cdef list ac_patterns
    cdef list regex_patterns
    
    # 公共方法
    cpdef void build(self, list patterns, list regex)
    cpdef list feed(self, bytes chunk)
    cpdef list match(self, bytes text)
    cpdef void reset(self)
    cpdef uint32_t get_total_matches(self)
    cpdef bint is_streaming(self)

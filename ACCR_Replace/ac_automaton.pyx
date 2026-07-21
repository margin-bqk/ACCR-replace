"""
简化的 AC automaton 实现
使用 Python 对象简化内存管理
"""

from libc.stdint cimport uint32_t
from cpython.bytes cimport PyBytes_AsString
import cython

# 常量定义
DEF ALPHABET_SIZE = 256


cdef class ACAutomaton:
    """简化的 AC automaton 实现"""
    
    def __cinit__(self):
        """初始化 automaton"""
        self.patterns = []
        self.built = False
        self.node_count = 0
    
    cpdef void build(self, list patterns):
        """构建 automaton"""
        self.patterns = patterns
        self.built = True
        self.node_count = len(patterns)
    
    cpdef list search(self, bytes text):
        """搜索文本中的模式"""
        if not self.built:
            return []
        
        cdef char* text_bytes = PyBytes_AsString(text)
        cdef uint32_t text_len = len(text)
        cdef list matches = []
        cdef uint32_t i, j
        cdef bytes pattern_bytes
        cdef uint32_t pattern_len
        cdef bint match_found
        
        # 简单的子字符串搜索
        for pattern in self.patterns:
            pattern_bytes = pattern.encode('utf-8')
            pattern_len = len(pattern_bytes)
            
            for i in range(text_len - pattern_len + 1):
                match_found = True
                for j in range(pattern_len):
                    if text_bytes[i + j] != pattern_bytes[j]:
                        match_found = False
                        break
                
                if match_found:
                    matches.append({
                        'pattern': pattern,
                        'start': i,
                        'end': i + pattern_len,
                        'type': 'ac'
                    })
        
        return matches
    
    cpdef uint32_t get_node_count(self):
        """获取节点数量"""
        return self.node_count

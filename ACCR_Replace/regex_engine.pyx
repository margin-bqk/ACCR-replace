"""
简化的 regex engine 实现
使用 Python re 模块简化实现
"""

from libc.stdint cimport uint32_t
import cython
import re


cdef class RegexEngine:
    """简化的正则表达式引擎"""
    
    def __cinit__(self):
        """初始化引擎"""
        self.patterns = []
        self.compiled_patterns = []
        self.built = False
    
    cpdef void build(self, list patterns):
        """构建正则表达式引擎"""
        self.patterns = patterns
        self.compiled_patterns = []
        
        for pattern in patterns:
            try:
                compiled = re.compile(pattern)
                self.compiled_patterns.append(compiled)
            except re.error:
                # 跳过无效的正则表达式
                pass
        
        self.built = True
    
    cpdef list match(self, bytes text):
        """匹配文本中的正则表达式"""
        if not self.built:
            return []
        
        cdef list matches = []
        cdef str text_str = text.decode('utf-8')
        
        for compiled in self.compiled_patterns:
            for match_obj in compiled.finditer(text_str):
                matches.append({
                    'pattern': compiled.pattern,
                    'start': match_obj.start(),
                    'end': match_obj.end(),
                    'matched': match_obj.group(),
                    'type': 'regex'
                })
        
        return matches

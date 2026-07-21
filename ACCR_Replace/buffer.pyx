"""
简化的 stream buffer 实现
使用 Python 字节对象简化实现
"""

from libc.stdint cimport uint32_t
import cython

# 常量定义
DEF DEFAULT_BUFFER_SIZE = 1024


cdef class StreamBuffer:
    """简化的流式缓冲区"""
    
    def __cinit__(self):
        """初始化缓冲区"""
        self.buffer = b""
        self.position = 0
    
    cpdef void reset(self):
        """重置缓冲区"""
        self.buffer = b""
        self.position = 0
    
    cpdef void append(self, bytes data):
        """添加数据到缓冲区"""
        self.buffer += data
    
    cpdef bytes get_data(self):
        """获取缓冲区数据"""
        return self.buffer
    
    cpdef uint32_t get_size(self):
        """获取缓冲区大小"""
        return len(self.buffer)
    
    cpdef uint32_t get_capacity(self):
        """获取缓冲区容量"""
        return DEFAULT_BUFFER_SIZE

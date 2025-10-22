"""
Simplified stream buffer implementation in Cython
Basic buffer functionality for streaming mode
"""

from libc.stdint cimport uint32_t
import cython


cdef class StreamBuffer:
    """Simplified stream buffer for incremental data processing"""
    
    def __cinit__(self):
        """Initialize the stream buffer"""
        self.buffer = b""
        self.position = 0
    
    cpdef void reset(self):
        """Reset the buffer"""
        self.buffer = b""
        self.position = 0
    
    cpdef void append(self, bytes data):
        """Append data to buffer"""
        self.buffer += data
    
    cpdef bytes get_data(self):
        """Get current buffer data"""
        return self.buffer
    
    cpdef uint32_t get_size(self):
        """Get buffer size"""
        return len(self.buffer)
    
    cpdef uint32_t get_capacity(self):
        """Get buffer capacity (simplified)"""
        return 1024  # Fixed capacity for simplicity

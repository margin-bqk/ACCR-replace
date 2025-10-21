# Buffer Cython definitions
# Defines circular buffer for streaming input processing

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memcpy, memset

# Circular buffer structure for streaming input
ctypedef struct CircularBuffer:
    char* data
    uint32_t size
    uint32_t capacity
    uint32_t read_pos
    uint32_t write_pos
    uint32_t is_full

# Main Buffer class for streaming processing
cdef class StreamBuffer:
    cdef CircularBuffer buffer
    cdef uint32_t default_capacity
    
    # Core methods
    cdef void _init_buffer(self, uint32_t capacity) nogil
    cdef void _free_buffer(self) nogil
    cdef uint32_t _write(self, char* data, uint32_t data_len) nogil
    cdef uint32_t _read(self, char* output, uint32_t output_len) nogil
    cdef uint32_t _peek(self, char* output, uint32_t output_len) nogil
    cdef void _clear(self) nogil
    cdef uint32_t _get_available_space(self) nogil
    cdef uint32_t _get_available_data(self) nogil
    
    # Public methods
    cpdef void initialize(self, uint32_t capacity=8192)
    cpdef uint32_t write(self, bytes data)
    cpdef bytes read(self, uint32_t length=0)
    cpdef bytes peek(self, uint32_t length=0)
    cpdef void clear(self)
    cpdef uint32_t get_available_space(self)
    cpdef uint32_t get_available_data(self)
    cpdef uint32_t get_capacity(self)

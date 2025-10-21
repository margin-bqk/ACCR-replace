# Buffer implementation
# Circular buffer for streaming input processing

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memcpy, memset
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AsString
import cython

# Import definitions
cimport buffer

cdef class StreamBuffer:
    """
    Circular buffer for efficient streaming data processing
    Supports continuous read/write operations with wrap-around
    """
    
    def __cinit__(self):
        """Initialize the buffer with default values"""
        self.buffer.data = NULL
        self.buffer.capacity = 0
        self.buffer.size = 0
        self.buffer.read_pos = 0
        self.buffer.write_pos = 0
        self.buffer.is_full = 0
        self.default_capacity = 8192  # 8KB default capacity
    
    def __dealloc__(self):
        """Clean up buffer memory when object is destroyed"""
        self._free_buffer()
    
    cpdef void initialize(self, uint32_t capacity=8192):
        """
        Initialize the buffer with specified capacity
        
        Args:
            capacity: Buffer capacity in bytes
        """
        if capacity == 0:
            capacity = self.default_capacity
        
        self._free_buffer()  # Free existing buffer if any
        self._init_buffer(capacity)
    
    cdef void _init_buffer(self, uint32_t capacity) nogil:
        """Initialize the circular buffer with given capacity"""
        self.buffer.data = <char*>PyMem_Malloc(capacity)
        if self.buffer.data:
            memset(self.buffer.data, 0, capacity)
            self.buffer.capacity = capacity
            self.buffer.size = 0
            self.buffer.read_pos = 0
            self.buffer.write_pos = 0
            self.buffer.is_full = 0
    
    cdef void _free_buffer(self) nogil:
        """Free the buffer memory"""
        if self.buffer.data:
            PyMem_Free(self.buffer.data)
            self.buffer.data = NULL
            self.buffer.capacity = 0
            self.buffer.size = 0
            self.buffer.read_pos = 0
            self.buffer.write_pos = 0
            self.buffer.is_full = 0
    
    cpdef uint32_t write(self, bytes data):
        """
        Write data to the buffer
        
        Args:
            data: Bytes data to write
            
        Returns:
            Number of bytes actually written
        """
        cdef char* data_bytes = PyBytes_AsString(data)
        cdef uint32_t data_len = len(data)
        return self._write(data_bytes, data_len)
    
    cdef uint32_t _write(self, char* data, uint32_t data_len) nogil:
        """Internal write implementation"""
        if not self.buffer.data or data_len == 0:
            return 0
        
        cdef uint32_t available_space = self._get_available_space()
        cdef uint32_t bytes_to_write = data_len if data_len <= available_space else available_space
        
        if bytes_to_write == 0:
            return 0
        
        # Calculate how much we can write before wrap-around
        cdef uint32_t first_chunk = self.buffer.capacity - self.buffer.write_pos
        if first_chunk > bytes_to_write:
            first_chunk = bytes_to_write
        
        # Write first chunk
        memcpy(self.buffer.data + self.buffer.write_pos, data, first_chunk)
        
        # Write second chunk if needed (wrap-around)
        if first_chunk < bytes_to_write:
            memcpy(self.buffer.data, data + first_chunk, bytes_to_write - first_chunk)
        
        # Update positions and size
        self.buffer.write_pos = (self.buffer.write_pos + bytes_to_write) % self.buffer.capacity
        self.buffer.size += bytes_to_write
        
        # Check if buffer is full
        if self.buffer.size == self.buffer.capacity:
            self.buffer.is_full = 1
        
        return bytes_to_write
    
    cpdef bytes read(self, uint32_t length=0):
        """
        Read data from the buffer
        
        Args:
            length: Number of bytes to read (0 = read all available)
            
        Returns:
            Bytes data read from buffer
        """
        cdef uint32_t available_data = self._get_available_data()
        cdef uint32_t bytes_to_read = length if length > 0 and length <= available_data else available_data
        
        if bytes_to_read == 0:
            return b""
        
        # Create output buffer
        cdef char* output = <char*>PyMem_Malloc(bytes_to_read)
        if not output:
            return b""
        
        cdef uint32_t bytes_read = self._read(output, bytes_to_read)
        cdef bytes result
        
        if bytes_read > 0:
            result = PyBytes_FromStringAndSize(output, bytes_read)
        else:
            result = b""
        
        PyMem_Free(output)
        return result
    
    cdef uint32_t _read(self, char* output, uint32_t output_len) nogil:
        """Internal read implementation"""
        if not self.buffer.data or output_len == 0:
            return 0
        
        cdef uint32_t available_data = self._get_available_data()
        cdef uint32_t bytes_to_read = output_len if output_len <= available_data else available_data
        
        if bytes_to_read == 0:
            return 0
        
        # Calculate how much we can read before wrap-around
        cdef uint32_t first_chunk = self.buffer.capacity - self.buffer.read_pos
        if first_chunk > bytes_to_read:
            first_chunk = bytes_to_read
        
        # Read first chunk
        memcpy(output, self.buffer.data + self.buffer.read_pos, first_chunk)
        
        # Read second chunk if needed (wrap-around)
        if first_chunk < bytes_to_read:
            memcpy(output + first_chunk, self.buffer.data, bytes_to_read - first_chunk)
        
        # Update positions and size
        self.buffer.read_pos = (self.buffer.read_pos + bytes_to_read) % self.buffer.capacity
        self.buffer.size -= bytes_to_read
        self.buffer.is_full = 0
        
        return bytes_to_read
    
    cpdef bytes peek(self, uint32_t length=0):
        """
        Peek at data in the buffer without consuming it
        
        Args:
            length: Number of bytes to peek (0 = peek all available)
            
        Returns:
            Bytes data from buffer (not consumed)
        """
        cdef uint32_t available_data = self._get_available_data()
        cdef uint32_t bytes_to_peek = length if length > 0 and length <= available_data else available_data
        
        if bytes_to_peek == 0:
            return b""
        
        # Create output buffer
        cdef char* output = <char*>PyMem_Malloc(bytes_to_peek)
        if not output:
            return b""
        
        cdef uint32_t bytes_peeked = self._peek(output, bytes_to_peek)
        cdef bytes result
        
        if bytes_peeked > 0:
            result = PyBytes_FromStringAndSize(output, bytes_peeked)
        else:
            result = b""
        
        PyMem_Free(output)
        return result
    
    cdef uint32_t _peek(self, char* output, uint32_t output_len) nogil:
        """Internal peek implementation (doesn't update read position)"""
        if not self.buffer.data or output_len == 0:
            return 0
        
        cdef uint32_t available_data = self._get_available_data()
        cdef uint32_t bytes_to_peek = output_len if output_len <= available_data else available_data
        
        if bytes_to_peek == 0:
            return 0
        
        # Calculate how much we can peek before wrap-around
        cdef uint32_t first_chunk = self.buffer.capacity - self.buffer.read_pos
        if first_chunk > bytes_to_peek:
            first_chunk = bytes_to_peek
        
        # Copy first chunk
        memcpy(output, self.buffer.data + self.buffer.read_pos, first_chunk)
        
        # Copy second chunk if needed (wrap-around)
        if first_chunk < bytes_to_peek:
            memcpy(output + first_chunk, self.buffer.data, bytes_to_peek - first_chunk)
        
        return bytes_to_peek
    
    cpdef void clear(self):
        """Clear the buffer (reset all positions)"""
        self._clear()
    
    cdef void _clear(self) nogil:
        """Internal clear implementation"""
        if self.buffer.data:
            memset(self.buffer.data, 0, self.buffer.capacity)
        self.buffer.size = 0
        self.buffer.read_pos = 0
        self.buffer.write_pos = 0
        self.buffer.is_full = 0
    
    cpdef uint32_t get_available_space(self):
        """Get available space in buffer"""
        return self._get_available_space()
    
    cdef uint32_t _get_available_space(self) nogil:
        """Internal available space calculation"""
        if not self.buffer.data:
            return 0
        return self.buffer.capacity - self.buffer.size
    
    cpdef uint32_t get_available_data(self):
        """Get available data in buffer"""
        return self._get_available_data()
    
    cdef uint32_t _get_available_data(self) nogil:
        """Internal available data calculation"""
        if not self.buffer.data:
            return 0
        return self.buffer.size
    
    cpdef uint32_t get_capacity(self):
        """Get buffer capacity"""
        return self.buffer.capacity

# Main Matcher Cython definitions
# Defines the main Matcher class that combines AC automaton and regex engine

from libc.stdint cimport uint32_t, uint64_t

# Match result structure for Python interface
ctypedef struct PyMatchResult:
    char* type
    char* pattern
    uint32_t start
    uint32_t end
    char* matched_text
    char* context

# Main Matcher class
cdef class Matcher:
    cdef object ac_automaton
    cdef object regex_engine
    cdef object stream_buffer
    cdef bint streaming_mode
    cdef uint32_t total_matches
    cdef list ac_patterns
    cdef list regex_patterns
    
    # Core methods
    cdef void _initialize_engines(self) nogil
    cdef list _process_chunk(self, char* chunk, uint32_t chunk_len) nogil
    cdef list _combine_matches(self, list ac_matches, list regex_matches) nogil
    
    # Public methods
    cpdef void build(self, list patterns=*, list regex=*)
    cpdef list feed(self, bytes chunk)
    cpdef list match(self, bytes text)
    cpdef void reset(self)
    cpdef uint32_t get_total_matches(self)
    cpdef bint is_streaming(self)

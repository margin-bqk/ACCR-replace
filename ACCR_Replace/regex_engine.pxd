# Regex Engine Cython definitions
# Defines the interface for PCRE2-based regular expression matching

from libc.stdint cimport uint32_t, uint64_t

# PCRE2 match result structure
ctypedef struct RegexMatch:
    uint32_t start
    uint32_t end
    uint32_t pattern_id
    char* pattern
    char* matched_text

# Main Regex Engine class
cdef class RegexEngine:
    cdef list compiled_patterns
    cdef list pattern_strings
    cdef dict pattern_to_id
    
    # Core methods
    cdef void _compile_patterns(self, list patterns) nogil
    cdef list _match_single(self, char* text, uint32_t text_len, uint32_t pattern_id) nogil
    cdef list _match_all(self, char* text, uint32_t text_len) nogil
    
    # Public methods
    cpdef void build(self, list patterns)
    cpdef list match(self, bytes text, int pattern_id=-1)
    cpdef uint32_t get_pattern_count(self)

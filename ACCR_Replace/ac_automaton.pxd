# AC Automaton Cython definitions
# Defines the data structures and methods for the Aho-Corasick automaton

from libc.stdint cimport uint32_t, uint64_t
from cpython.mem cimport PyMem_Malloc, PyMem_Free

# Match result structure
ctypedef struct MatchResult:
    uint32_t start
    uint32_t end
    uint32_t pattern_id
    char* pattern

# AC Automaton node structure
ctypedef struct ACNode:
    ACNode** children
    ACNode* fail
    uint32_t* output
    uint32_t output_count
    uint32_t is_final
    char character

# Main AC Automaton class
cdef class ACAutomaton:
    cdef ACNode* root
    cdef uint32_t node_count
    cdef list patterns
    cdef dict pattern_to_id
    
    # Core methods
    cdef void _build_goto(self, list patterns) nogil
    cdef void _build_failure_links(self) nogil
    cdef void _collect_outputs(self) nogil
    cdef list _search(self, char* text, uint32_t text_len) nogil
    
    # Public methods
    cpdef void build(self, list patterns)
    cpdef list search(self, bytes text)
    cpdef uint32_t get_node_count(self)

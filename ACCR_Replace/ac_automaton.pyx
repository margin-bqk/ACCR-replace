"""
Simplified AC automaton implementation in Cython
Basic functionality without complex memory management
"""

from libc.stdint cimport uint32_t
from cpython.bytes cimport PyBytes_AsString
import cython


cdef class ACAutomaton:
    """Simplified AC automaton for multi-pattern matching"""
    
    def __cinit__(self):
        """Initialize the automaton"""
        self.patterns = []
        self.built = False
    
    cpdef void build(self, list patterns):
        """Build the automaton from patterns"""
        self.patterns = patterns
        self.built = True
    
    cpdef list search(self, bytes text, uint32_t text_len=0):
        """Search for patterns in text (simplified implementation)"""
        if not self.built:
            return []
        
        cdef char* text_bytes = PyBytes_AsString(text)
        cdef uint32_t actual_len = text_len if text_len > 0 else len(text)
        cdef list matches = []
        cdef uint32_t i, j, k
        cdef char* pattern_bytes
        cdef uint32_t pattern_len
        
        # Simple substring search for each pattern
        for i, pattern in enumerate(self.patterns):
            pattern_bytes = PyBytes_AsString(pattern.encode('utf-8'))
            pattern_len = len(pattern)
            
            for j in range(actual_len - pattern_len + 1):
                cdef bint match_found = True
                for k in range(pattern_len):
                    if text_bytes[j + k] != pattern_bytes[k]:
                        match_found = False
                        break
                
                if match_found:
                    matches.append({
                        'pattern': pattern,
                        'start': j,
                        'end': j + pattern_len
                    })
        
        return matches
    
    cpdef uint32_t get_node_count(self):
        """Get node count (simplified)"""
        return len(self.patterns)
